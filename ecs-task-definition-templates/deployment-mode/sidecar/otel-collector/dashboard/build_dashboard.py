#!/usr/bin/env python3
"""
Generates a CloudWatch PromQL dashboard body for the collector configuration in
collector-ecs-metrics.yaml (awsecscontainermetrics receiver, native metric names).

Metric names and resource attributes are the receiver's own (ecs.task.*, container.*,
aws.ecs.*). Utilization percentages are computed in PromQL from utilized / reserved.
Units: CPU in ECS CPU units (1024 = 1 vCPU); memory in MiB; network rates in bytes/s;
storage bytes are cumulative (rate() applied). With awsvpc networking, container network
metrics report the task's shared interface, so they are never summed across containers.

Every filter is a CloudWatch pattern variable substituted into a regex matcher,
defaulting to ".*" (which also matches series without the label).

Usage:
    python3 build_dashboard.py [--region us-west-2] [--out dashboard.json]
"""
import argparse
import json

R = "@resource."
CLUSTER = R + "aws.ecs.cluster.name"
SERVICE = R + "aws.ecs.service.name"
FAMILY = R + "aws.ecs.task.family"
TASK_ID = R + "aws.ecs.task.id"
CONTAINER = R + "container.name"
LAUNCH = R + "aws.ecs.task.launch_type"

# (variable id, label, placeholder token, PromQL label, scope, default)
FILTERS = [
    ("cluster",   "Cluster",           "VAR_CLUSTER",   CLUSTER,   "task",      ".*"),
    ("service",   "Service",           "VAR_SERVICE",   SERVICE,   "task",      ".*"),
    ("family",    "Task family",       "VAR_FAMILY",    FAMILY,    "task",      ".*"),
    ("launch",    "Launch type",       "VAR_LAUNCH",    LAUNCH,    "task",      ".*"),
    ("container", "Container name",    "VAR_CONTAINER", CONTAINER, "container", ".*"),
]

# Not referenced by m(); container metrics are recognised by their "container." prefix.


def _matchers(scopes):
    return ", ".join(f'"{lbl}"=~"{tok}"' for _, _, tok, lbl, sc, _ in FILTERS if sc in scopes)


TASK_MATCH = _matchers({"task"})
CTR_MATCH = _matchers({"task", "container"})


def m(metric):
    base = CTR_MATCH if metric.startswith("container.") else TASK_MATCH
    return "{" + f'"{metric}", {base}' + "}"


def by(*labels):
    return "by (" + ", ".join(f'"{l}"' for l in labels) + ")"


# ---------------------------------------------------------------- layout ----
class Layout:
    def __init__(self):
        self.widgets, self.x, self.y, self.row_h = [], 0, 0, 0

    def newline(self):
        if self.x:
            self.y += self.row_h
        self.x, self.row_h = 0, 0

    def add(self, widget, w, h):
        if self.x + w > 24:
            self.newline()
        widget.update(x=self.x, y=self.y, width=w, height=h)
        self.widgets.append(widget)
        self.x += w
        self.row_h = max(self.row_h, h)

    def section(self, title, md=""):
        self.newline()
        self.add({"type": "text", "properties": {"markdown": f"## {title}\n{md}".rstrip(),
                                                 "background": "transparent"}}, 24, 2 if md else 1)
        self.newline()


STYLE_KEYS = {"lineOptions", "barOptions", "pieOptions", "numberOptions", "gaugeOptions"}
LINE_DEFAULTS = {"width": 2, "pattern": "solid", "spline": False, "filled": False, "stacked": False}
NUM = {"numberOptions": {"sparkline": True, "truncate": True}}
GAUGE = {"gaugeOptions": {"min": 0, "max": 100}}
WARN = {"annotations": {"horizontal": [{"type": "static", "label": "80%", "value": 80, "color": "#d62728"}]}}
PIE = {"pieOptions": {"innerSize": "50%"}}


def q(qid, expr, label=None):
    d = {"id": qid, "type": "cloudwatch-metrics", "language": "PromQL", "query": expr, "step": 60}
    if label:
        d["label"] = label
    return d


def chart(title, queries, view="line", plot=None, desc=None):
    props = {"view": view, "title": title, "region": REGION, "data": {"queries": queries},
             "plotOptions": {"legend": {"position": "bottom", "show": view not in ("number", "solidgauge")}}}
    if desc:
        props["description"] = desc
    plot = dict(plot or {})
    style = {k: plot.pop(k) for k in list(plot) if k in STYLE_KEYS}
    if view == "line":
        style["lineOptions"] = {**LINE_DEFAULTS, **style.get("lineOptions", {})}
    props["plotOptions"].update(plot)
    props["plotOptions"]["style"] = style
    return {"type": "chart", "properties": props}


def pct():
    return {"yAxis": [{"min": 0, "title": "%", "showUnits": False}], **WARN}


def axis(title):
    return {"yAxis": [{"min": 0, "title": title, "showUnits": True}]}


# ----------------------------------------------------------- expressions ----
def ratio(num, den, labels=()):
    b = f" {by(*labels)} " if labels else ""
    return f"100 * sum{b}({m(num)}) / sum{b}({m(den)} > 0)"


def count_tasks(*labels):
    inner = by(*labels, TASK_ID)
    return f"count {by(*labels)} (count {inner} ({m('ecs.task.memory.utilized')}))" if labels \
        else f"count(count {inner} ({m('ecs.task.memory.utilized')}))"


def count_distinct(label):
    return f"count(count {by(label)} ({m('ecs.task.memory.utilized')}))"


VCPU = " / 1024"


def build(region):
    global REGION
    REGION = region
    L = Layout()

    L.add({"type": "text", "properties": {"markdown": (
        "# Amazon ECS metrics (PromQL)\n"
        "Metrics from the `awsecscontainermetrics` receiver (`collector-ecs-metrics.yaml`, 60s collection). "
        "**Filters are regexes** (default `.*`; e.g. `checkout|payments`). Container name applies to container "
        "panels only. CPU shown in vCPU (ECS CPU units / 1024)."
    )}}, 24, 2)

    # ---------------- Cluster overview ----------------
    L.section("Cluster overview")
    L.add(chart("Running tasks (RunningTaskCount)", [q("a", count_tasks())], "number", NUM), 4, 4)
    L.add(chart("Services (ServiceCount)", [q("a", count_distinct(SERVICE))], "number", NUM), 4, 4)
    L.add(chart("Running containers", [q("a", f"count(count {by(TASK_ID, CONTAINER)} ({m('container.memory.utilized')}))")], "number", NUM), 4, 4)
    L.add(chart("Task families", [q("a", count_distinct(FAMILY))], "number", NUM), 4, 4)
    L.add(chart("CPU utilization %", [q("a", ratio("ecs.task.cpu.utilized", "ecs.task.cpu.reserved"))], "solidgauge", GAUGE), 4, 4)
    L.add(chart("Memory utilization %", [q("a", ratio("ecs.task.memory.utilized", "ecs.task.memory.reserved"))], "solidgauge", GAUGE), 4, 4)

    L.add(chart("CPU utilized vs reserved (vCPU)", [
        q("u", f"sum {by(CLUSTER)} ({m('ecs.task.cpu.utilized')}){VCPU}", "ecs.task.cpu.utilized"),
        q("r", f"sum {by(CLUSTER)} ({m('ecs.task.cpu.reserved')}){VCPU}", "ecs.task.cpu.reserved"),
    ], plot=axis("vCPU")), 8, 6)
    L.add(chart("Memory utilized vs reserved (MiB)", [
        q("u", f"sum {by(CLUSTER)} ({m('ecs.task.memory.utilized')})", "ecs.task.memory.utilized"),
        q("r", f"sum {by(CLUSTER)} ({m('ecs.task.memory.reserved')})", "ecs.task.memory.reserved"),
    ], plot=axis("MiB")), 8, 6)
    L.add(chart("Running tasks by cluster", [q("a", count_tasks(CLUSTER))], plot=axis("tasks")), 8, 6)
    L.add(chart("Network Rx / Tx (bytes/s)", [
        q("rx", f"sum {by(CLUSTER)} ({m('ecs.task.network.rate.rx')})", "NetworkRxBytes"),
        q("tx", f"sum {by(CLUSTER)} ({m('ecs.task.network.rate.tx')})", "NetworkTxBytes"),
    ], plot=axis("B/s")), 12, 6)
    L.add(chart("Storage read / write (bytes/s)", [
        q("r", f"sum {by(CLUSTER)} (rate({m('ecs.task.storage.read_bytes')}[5m]))", "StorageReadBytes"),
        q("w", f"sum {by(CLUSTER)} (rate({m('ecs.task.storage.write_bytes')}[5m]))", "StorageWriteBytes"),
    ], plot=axis("B/s")), 12, 6)

    # ---------------- Services ----------------
    L.section("Services")
    L.add(chart("CPU utilization % by service", [q("a", ratio("ecs.task.cpu.utilized", "ecs.task.cpu.reserved", (CLUSTER, SERVICE)))], plot=pct()), 12, 6)
    L.add(chart("Memory utilization % by service", [q("a", ratio("ecs.task.memory.utilized", "ecs.task.memory.reserved", (CLUSTER, SERVICE)))], plot=pct()), 12, 6)
    L.add(chart("Running tasks by service", [q("a", count_tasks(CLUSTER, SERVICE))], plot=axis("tasks")), 8, 6)
    L.add(chart("Network Rx by service (bytes/s)", [q("a", f"sum {by(SERVICE)} ({m('ecs.task.network.rate.rx')})")], plot=axis("B/s")), 8, 6)
    L.add(chart("Network Tx by service (bytes/s)", [q("a", f"sum {by(SERVICE)} ({m('ecs.task.network.rate.tx')})")], plot=axis("B/s")), 8, 6)
    L.add(chart("Tasks by task family", [q("a", count_tasks(FAMILY))], "pie", PIE), 12, 6)
    L.add(chart("Tasks by launch type", [q("a", count_tasks(LAUNCH))], "pie", PIE), 12, 6)

    # ---------------- Tasks ----------------
    L.section("Tasks", "Top 10 tasks. Utilization = utilized / reserved, computed in PromQL.")
    L.add(chart("Top tasks by CPU utilization % ", [
        q("a", f"topk(10, {ratio('ecs.task.cpu.utilized', 'ecs.task.cpu.reserved', (SERVICE, TASK_ID))})")], plot=pct()), 12, 6)
    L.add(chart("Top tasks by memory utilization % ", [
        q("a", f"topk(10, {ratio('ecs.task.memory.utilized', 'ecs.task.memory.reserved', (SERVICE, TASK_ID))})")], plot=pct()), 12, 6)
    L.add(chart("Top tasks by network Rx (bytes/s)", [
        q("a", f"topk(10, sum {by(SERVICE, TASK_ID)} ({m('ecs.task.network.rate.rx')}))")], plot=axis("B/s")), 12, 6)
    L.add(chart("Top tasks by memory utilized (MiB)", [
        q("a", f"topk(10, sum {by(SERVICE, TASK_ID)} ({m('ecs.task.memory.utilized')}))")], plot=axis("MiB")), 12, 6)

    # ---------------- Containers ----------------
    L.section("Containers", "Container name filter applies here. Container network is the task's shared namespace, so it is shown per container, not summed.")
    L.add(chart("Top containers by CPU utilization % ", [
        q("a", f"topk(10, {ratio('container.cpu.utilized', 'container.cpu.reserved', (SERVICE, CONTAINER, TASK_ID))})")], plot=pct()), 12, 6)
    L.add(chart("Top containers by memory utilization % ", [
        q("a", f"topk(10, {ratio('container.memory.utilized', 'container.memory.reserved', (SERVICE, CONTAINER, TASK_ID))})")], plot=pct()), 12, 6)
    L.add(chart("Container CPU utilized by container name (vCPU)", [
        q("a", f"sum {by(CONTAINER)} ({m('container.cpu.utilized')}){VCPU}")], plot=axis("vCPU")), 8, 6)
    L.add(chart("Container memory utilized by container name (MiB)", [
        q("a", f"sum {by(CONTAINER)} ({m('container.memory.utilized')})")], plot=axis("MiB")), 8, 6)
    L.add(chart("Container memory reserved by container name (MiB)", [
        q("a", f"sum {by(CONTAINER)} ({m('container.memory.reserved')})")], plot=axis("MiB")), 8, 6)
    L.add(chart("Container network Rx / Tx (bytes/s, per task namespace)", [
        q("rx", f"max {by(SERVICE, CONTAINER)} ({m('container.network.rate.rx')})", "rx"),
        q("tx", f"max {by(SERVICE, CONTAINER)} ({m('container.network.rate.tx')})", "tx"),
    ], plot=axis("B/s")), 12, 6)
    L.add(chart("Container storage read / write (bytes/s)", [
        q("r", f"sum {by(CONTAINER)} (rate({m('container.storage.read_bytes')}[5m]))", "read"),
        q("w", f"sum {by(CONTAINER)} (rate({m('container.storage.write_bytes')}[5m]))", "write"),
    ], plot=axis("B/s")), 12, 6)

    variables = [{"type": "property", "property": "region", "inputType": "input", "id": "region",
                  "label": "Region", "defaultValue": region, "visible": True}]
    for vid, label, tok, _, _, default in FILTERS:
        v = {"type": "pattern", "pattern": tok, "inputType": "input", "id": vid,
             "label": label, "defaultValue": default, "visible": True}
        if vid == "launch":
            v.update(inputType="radio", values=[{"label": "All", "value": ".*"},
                                                {"label": "Fargate", "value": "FARGATE"},
                                                {"label": "EC2", "value": "EC2"},
                                                {"label": "Managed instances", "value": "MANAGED_INSTANCES"}])
        variables.append(v)
    return {"start": "-PT3H", "periodOverride": "inherit", "widgets": L.widgets, "variables": variables}


def defaults():
    """Placeholder -> default value, for validating queries outside the console."""
    return {tok: default for _, _, tok, _, _, default in FILTERS}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--region", default="us-west-2")
    ap.add_argument("--out", default="dashboard.json")
    a = ap.parse_args()
    body = build(a.region)
    with open(a.out, "w") as f:
        json.dump(body, f, indent=2)
    print(f"wrote {a.out}: {len(body['widgets'])} widgets, {len(body['variables'])} variables")
