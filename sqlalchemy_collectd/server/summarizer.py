# TODO: most of this should be replaced by protocol.Values and generic
# translation functions set up in types.py for "internal types" vs.
# "external types"; this will be one of the stream translators


import collectd

from .. import types as internal_types


_summarizers = {}


def summarize(receiver, timestamp):
    if receiver.aggregator.interval is None:
        return

    for type_ in receiver.internal_types:
        summarizer = _summarizers.get(type_, None)
        if summarizer:
            summarizer(receiver, type_, timestamp)


def summarizes(protocol_type):
    def decorate(fn):
        _summarizers[protocol_type] = fn
        return fn

    return decorate


@summarizes(internal_types.pool_internal)
def _summarize_pool_stats(receiver, type_, timestamp):
    values = collectd.Values(
        type="count",
        plugin=receiver.plugin,
        time=timestamp,
        interval=receiver.aggregator.interval,
    )
    for (
        hostname,
        progname,
        stats,
    ) in receiver.aggregator.get_stats_by_progname(type_.name, timestamp, sum):
        print("Summarize values by progname: %s" % stats)
        for name, value in zip(type_.names, stats.values):
            values.dispatch(
                host=hostname,
                plugin_instance=progname,
                type_instance=name,
                values=[value],
            )

    for hostname, stats in receiver.aggregator.get_stats_by_hostname(
        type_.name, timestamp, sum
    ):
        print("Summarize values by hostname: %s" % stats)
        for name, value in zip(type_.names, stats.values):
            values.dispatch(
                host=hostname,
                plugin_instance="host",
                type_instance=name,
                values=[value],
            )


@summarizes(internal_types.totals_internal)
def _summarize_totals(receiver, type_, timestamp):
    values = collectd.Values(
        type="derive",
        plugin=receiver.plugin,
        time=timestamp,
        interval=receiver.aggregator.interval,
    )

    for (
        hostname,
        progname,
        stats,
    ) in receiver.aggregator.get_stats_by_progname(type_.name, timestamp, sum):
        print("Summarize totals by progname: %s" % stats)
        for name, value in zip(type_.names, stats.values):
            values.dispatch(
                host=hostname,
                plugin_instance=progname,
                type_instance=name,
                values=[value],
            )

    for hostname, stats in receiver.aggregator.get_stats_by_hostname(
        type_.name, timestamp, sum
    ):
        print("Summarize totals by hostname: %s" % stats)
        for name, value in zip(type_.names, stats.values):
            values.dispatch(
                host=hostname,
                plugin_instance="host",
                type_instance=name,
                values=[value],
            )
