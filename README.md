# Sumo Logic collectd Plugin

A [collectd](https://collectd.org/) output plugin to send Carbon 2.0-formatted metrics to Sumo Logic.

## Get Started

### 1. Python version

Sumo Logic collectd plugin is built on top of [collectd-python plugin](https://collectd.org/documentation/manpages/collectd-python.5.shtml).
The minimum required version for running the plugin is Python version 2.6.
You can download and install the desired Python version from [Python download page](https://www.python.org/downloads/).

### 2. Install collectd on your machine

If collectd is already installed, you can skip this step.
Otherwise, follow the instructions in the [collectd download](https://collectd.org/download.shtml) site for download and installation.
For additional details, see [First steps](https://collectd.org/wiki/index.php/First_steps) section in the collectd Wiki.

#### MacOS

```sh
brew install collectd
```

#### Debian / Ubuntu

```sh
sudo apt-get install collectd
```

### 3. Download and install Sumo Logic collectd plugin

#### Option 1: Install as a library

```sh
sudo pip install sumologic_collectd_metrics
```

All required dependencies will be automatically installed with library installation.

#### Option 2: Install with source code

The Sumo Logic collectd plugin source code can be saved in a directory anywhere on your system.
Download it from [Python Package Index](https://pypi.python.org/pypi/sumologic_collectd_metrics),
or:

```sh
git clone https://github.com/SumoLogic/sumologic-collectd-plugin.git
```

Sumo Logic collectd plugin uses [requests](http://docs.python-requests.org/en/master/)
and [retry](https://pypi.python.org/pypi/retrying) libraries for sumbitting HTTPS requests.
If they are not installed. Install them using pip:

```sh
sudo pip install requests
sudo pip install retry
```

### 4. Create an HTTP Metrics Source in Sumo Logic

Create a [Sumo Logic account](https://www.sumologic.com/) if you don't currently have one.

Follow these instructions for [setting up an HTTP Source](https://help.sumologic.com/Send-Data/Sources/02Sources-for-Hosted-Collectors/HTTP-Source/zGenerate-a-new-URL-for-an-HTTP-Source)
in Sumo Logic.
Be sure to obtain the URL endpoint after creating an HTTP Source.

### 5. Configure Sumo Logic collectd plugin

Sumo Logic collectd plugin supports the following parameters.
To configure the plugin, modify collectd's configuration file named `collectd.conf` (e.g. `/etc/collectd/collectd.conf`).

#### Required parameters

The parameters below are required and must be specified in the module
config.

| Name                                                                                                                                   | Description                                                                                                                                                                                                                              | Type   | Required |
| -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | -------- |
| [URL](https://help.sumologic.com/Send-Data/Sources/02Sources-for-Hosted-Collectors/HTTP-Source/zGenerate-a-new-URL-for-an-HTTP-Source) | The URL to send metrics to. This should be given when [creating the HTTP Source](https://help.sumologic.com/Send-Data/Sources/02Sources-for-Hosted-Collectors/HTTP-Source/zGenerate-a-new-URL-for-an-HTTP-Source) on Sumo Logic web app. | String | True     |

#### Basic parameters

The parameters below are not strictly required. It is recommended to set
these parameters as they prove to be extremely useful to categorize your
metrics and search by them.

| Name                     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Type                                                       | Required |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------- | -------- |
| SourceName               | Name of the metrics source. `_sourceName` can be used to search metrics from this source. It will override the default configured in the the Sumo Logic Source configuration.                                                                                                                                                                                                                                                                                                  | String                                                     | False    |
| SourceHost               | Name of metrics host. `_sourceHost` can be used to search metrics from this host. It will override the default configured in the the Sumo Logic Source configuration.                                                                                                                                                                                                                                                                                                          | String                                                     | False    |
| SourceCategory           | Category of the collected metrics. `_sourceCategory` can be used to search metrics from this category. It will override the default configured in the the Sumo Logic Source configuration.                                                                                                                                                                                                                                                                                     | String                                                     | False    |
| Dimensions               | Key value pairs that contribute to identifying a metric. Collectd data have intrinsic dimensions with keys as `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `ds_name`, `ds_type`. The Additional dimensions specified here can help separating metrics collected from this collectd instance with metircs collected from other collectd instances. Dimensions cannot contain [Reserved symbols](#reserved-symbols) and [Reserved keywords](#reserved-keywords) | Srings in the format of `"key1"="val1", "key2"="val2"` ... | False    |
| Metadata                 | Key value pairs that do not contribute to identifying a metric. Metadata are primarily used to assist in searching metrics. Collectd data may have internal metadata. The additional metadata specified here can be used to enrich the existing metadata set. Metadata cannot contain [Reserved symbols](#reserved-symbols) and [Reserved keywords](#reserved-keywords)                                                                                                        | Srings in the format of `"key1"="val1", "key2"="val2"` ... | False    |
| AddMetricDimension       | If set to `true` adds new dimension named `metric` to every data point which consists of `type` and `type_instance` concatenated using `MetricDimensionSeparator`. By default it is set to `True`.                                                                                                                                                                                                                                                                             | Boolean                                                    | False    |
| MetricDimensionSeparator | String used to concatenate `type` and `type_instance` while creating `metric` dimension. See `AddMetricDimension` option. By default it is `.`.                                                                                                                                                                                                                                                                                                                                | String                                                     | False    |

#### Additional parameters

For additional configuration parameters, see [Advanced parameters](#advanced-parameters) below.

#### Example configuration

An example configuration for the plugin is shown below (code to be added to `collectd.conf` under `collectd_root/etc`):

```aconf
LoadPlugin python
<Plugin python>
    # Uncomment and update the following line if sumologic collectd plugin installed with source code
    # ModulePath "/path/to/sumologic-collectd-plugin"
    LogTraces true
    Interactive false
    Import "sumologic_collectd_metrics"

    <Module "sumologic_collectd_metrics">
        URL "https://<deployment>.sumologic.com/receiver/v1/http/<source_token>"  # URL must be specified
        # Uncomment and update the following lines to override the default metadata configured in the the Sumo Logic Source configuration
        # SourceName "my_source"
        # SourceHost "my_host"
        # SourceCategory "my_category"
        # Uncomment and update the following lines to add additional key=value pairs
        # Dimensions "my_dim_key1"="my_dim_val1", "my_dim_key2"="my_dim_val2"
        # Metadata "my_meta_key1"="my_meta_val1", "my_meta_key2"="my_meta_val2"
    </Module>
</Plugin>
```

#### Other recommended modules

It is recommeded to setup the following two plugins in `collectd.conf`.
The functionalities of the two plugins are explained in collectd Wiki
[Plugin:LogFile](https://collectd.org/wiki/index.php/Plugin:LogFile)
and [Plugin:CSV](https://collectd.org/wiki/index.php/Plugin:CSV):

```aconf
LoadPlugin logfile
<Plugin logfile>
    LogLevel "info"
    File "/var/log/collectd.log"
    Timestamp true
    PrintSeverity true
</Plugin>

LoadPlugin csv
<Plugin csv>
    DataDir "/usr/local/var/lib/collectd/csv"
</Plugin>
```

The following pulgins, if enabled in `collectd.conf`, enable collecting
[cpu](https://collectd.org/wiki/index.php/Plugin:CPU),
[memory](https://collectd.org/wiki/index.php/Plugin:Memory),
[disk](https://collectd.org/wiki/index.php/Plugin:Disk),
[network](https://collectd.org/wiki/index.php/Plugin:Interface)
metrics from the system:

```aconf
LoadPlugin cpu
LoadPlugin memory
LoadPlugin disk
LoadPlugin interface
```

A list of all collectd plugins is awailable in collectd Wiki [Table of
Plugins](https://collectd.org/wiki/index.php/Table_of_Plugins)

#### Reserved symbols

Equal sign and space are reserved symbols.

```console
"=" " "
```

#### Reserved keywords

Following terms are reserved for Sumo Logic internal use only:

```console
"_sourcehost", "_sourcename", "_sourcecategory", "_collectorid", "_collector", "_source", "_sourceid", "_contenttype", "_rawname"
```

### 6. Start sending metrics

Start sending metrics by running collectd, e.g. (command will differ
depending on collectd installation):

```sh
sudo service collectd start
```

#### View logs

If `logfile` plugin is installed, then you can view logs by tailling collectd.log
file, e.g. (command can be different depending on collectd installation):

```sh
tail -f /var/log/collectd.log
```

#### Data model

The Sumo Logic collectd plugin will send metrics using the [Carbon 2.0](http://metrics20.org/implementations/) format, defined as:

```console
dimensions  metadata value timestamp
```

`dimensions` and `metadata` are key/value pairs of strings separated by two spaces.
`dimensions` uniquely identifying a metric, while `metadata` do not contribute to identifying a metric.
Instead, they are used to categorize metrics for searching.
`value` is a double number.
`timestamp` is a 10-digit UNIX epoch timestamp.

Example data before compression:

```console
host=my_mac plugin=cpu plugin_instance=1 type=cpu type_instance=user ds_name=value ds_type=DERIVE  meta_key1=meta_val1 5991.000000 1502148249
host=my_mac plugin=cpu plugin_instance=0 type=cpu type_instance=user ds_name=value ds_type=DERIVE  meta_key1=meta_val1 98722.000000 1502148249
```

#### Naming Schema

Collectd uses a very powerful naming schema to identify each statistics value.
It has been proven very generic and flexible, but may be confusing at first, especially to new users.
You can read more about it by following this wiki [collectd naming schema](https://collectd.org/wiki/index.php/Naming_schema).

#### Compression

Metrics are batched and compressed before they are sent.
The default compression algorithm is `"deflate"`.
The algorithm is explained in more detail in [An Explanation of the Deflate Algorithm](https://zlib.net/feldspar.html).
Alternatively, you can specify `"gzip"` for gzip compression and `"none"` for no compression.

#### Error handling

Sumo Logic collectd plugin retries on exceptions by default.
When all retries fail, the request is either scheduled for a future attempt or dropped based on the buffer status.
By default, 1000 requests are buffered.
If the buffer becomes full, then requests failed after all retries will be dropped.
Otherwise, it is put back to the processing queue for the next run.

### 7. View metrics

To view the metrics sent by the collectd plugin, log into Sumo Logic and open a Metrics tab.
Query for metrics using either dimensions or metadata, e.g.:

```console
_sourceName=my_source _sourceHost=my_host _sourceCategory=my_category plugin=cpu
```

You should be able to see metrics displayed in the main graph.

## Advanced Topics

### Advanced parameters

You can configure the Sumo Logic collectd plugin by overriding default
values for plugin parameters.

| Name                  | Description                                                                                                                                                                                                                                                                                                                                                                          | Type                 | Default | Unit   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------- | ------- | ------ |
| MaxBatchSize          | Sumo Logic collectd plugin batches metrics before sending them over https. MaxBatchSize defines the upper limit of metrics per batch.                                                                                                                                                                                                                                                | Positive Integer     | 5000    | NA     |
| MaxBatchInterval      | Sumo Logic collectd plugin batches metrics before sending them through https. MaxBatchInterval defines the upper limit of duration to construct a batch.                                                                                                                                                                                                                             | Positive Integer     | 1       | Second |
| HttpPostInterval      | Sumo Logic collectd plugin schedules https post requests at fixed intervals. HttpPostInterval defines the frequency for the scheduler to run. If no metrics batch is available at the time, the sceduler immediately returns. If multiple metrics batches are available, then the oldest batch is picked to be sent.                                                                 | Positive Float       | 0.1     |        |
| MaxRequestsToBuffer   | Sumo Logic collectd plugin buffers failed and delayed metrics batch requests. MaxRequestsToBuffer specifies the maximum number of these requests to buffer. After the buffer becomes full, the request with oldest metrics batch will be dropped to make space for new metrics batch.|Positive Integer                                                                               | Positive Integer     | 1000    | NA     |
| RetryInitialDelay     | Sumo Logic collectd plugin retries on recoverable exceptions. RetryInitialDelay specifies the initial delay before a retry is scheduled. More information can be found in the retry library                                                                                                                                                                                          | Non-negative Integer | 0       | Second |
| RetryMaxAttempts      | Sumo Logic collectd plugin retries on recoverable exceptions. RetryMaxAttempts specifies the upper limit of retries before the current retry logic fails. The metric batch is then either put back for the next run (when metrics buffer specified by MaxRequestsToBuffer is not full), or dropped (when metrics buffer is full). More information can be found in the retry library | Positive Integer     | 10      | NA     |
| RetryMaxDelay         | Sumo Logic collectd plugin retries on recoverable exceptions. RetryMaxDelay specifies the upper limit of delay before the current retry logic fails. Then the metric batch either is put back for the next run (when metrics buffer specified by MaxRequestsToBuffer is not full), or dropped (when metrics buffer is full). More information can be found in the retry library      | Positive Integer     | 100     | Second |
| RetryJitterMin        | Sumo Logic collectd plugin retries on recoverable exceptions. RetryJitterMin specifies the minimum extra seconds added to delay between attempts. More information can be found in the retry library                                                                                                                                                                                 | Non-negative Integer | 0       | Second |
| RetryJitterMax        | Sumo Logic collectd plugin retries on recoverable exceptions. RetryJitterMax specifies the maximum extra seconds added to delay between attempts. More information can be found in the retry library                                                                                                                                                                                 | Non-negative Integer | 10      | Second |
| EnableInternalMetrics | Enable the plugin's internal metrics. See [Plugin Internal Metrics](#plugin-internal-metrics)                                                                                                                                                                                                                                                                                        | Boolean              | false   | NA     |
| SignalFxStatsDTags    | Enable extracting metadata from metrics using SignalFx' extension to the StatsD protocol. See: https://docs.signalfx.com/en/latest/integrations/agent/monitors/collectd-statsd.html#adding-dimensions-to-statsd-metrics                                                                                                                                                              | Boolean              | false   | NA     |

### Plugin Architecture

```console
Collectd        MetricsConverter                    MetricsBatcher         MetricsBuffer                               MetricsSender
--------        --------------------------          --------------         ------------------------                    -----------------
                                                                                                       batch to send   
Raw Data   ->   Metric in Carbon 2.0 format    ->   Metrics Batch     ->   Buffered metrics batches         ->         Request scheduler
                                                                                                            <-
                                                                                                       failed batch
```

### Plugin Internal Metrics

If the `EnableInternalMetrics` configuration option is set to true, the plugin emits metrics describing its own internal state.

The following metrics are available:

| Name             | Type  | Description                                                                                                  |
|------------------|-------|--------------------------------------------------------------------------------------------------------------|
| received_metrics | Gauge | The number of metrics values received from collectd.                                                         |
| sent_metrics     | Gauge | The number of metrics values successfully sent to Sumo.                                                      |
| sent_batches     | Gauge | The number of metrics batches successfully sent to Sumo.                                                     |
| dropped_metrics  | Gauge | The number of metrics values dropped during processing due to various faults, typically buffers being full.  |
| dropped_batches  | Gauge | The number of metrics batches dropped during processing due to various faults, typically buffers being full. |
| batch_queue_size | Gauge | The number of batches in the sending queue.                                                                  |

## TLS 1.2 Requirement

Sumo Logic only accepts connections from clients using TLS version 1.2 or greater.
To utilize the content of this repo, ensure that it's running in an execution environment that is configured to use TLS 1.2 or greater.

## License

The Sumo Logic collectd output plugin is published under the Apache Software License, Version 2.0.
Please visit http://www.apache.org/licenses/LICENSE-2.0.txt for details.
