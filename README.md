# Sumo Logic Collectd Output Plugin

This is a plugin for [collectd](https://collectd.org/).
It is fully free and fully open source. The license is Apache 2.0, meaning you are pretty much free to use it however you want in whatever way.

## Getting Started

### 1. Install collectd on you matchine

### 2. Install Sumo Logic output plugin into collectd

### 3. Setup Sumo Logic output plugin configurations
Sumo Logic output plugin supports following prarmeters. 
#### Required parameter
The paramer below is required and must be specified in the module config. 

|Name|Description|Type|Required|
|:---|:---|:---|:---|
|URL|The URL to send logs to. This should be given when creating a Metrics HTTP Source on Sumo Logic web app. See [Metrics Http Source](https://not_ready_yet)|String|True|

#### Basic parameters
The paramers below are not strictly required. It is recommended to set these parameters as they prove to be extremely useful to categorize your metrics and search by them.

|Name|Description|Type|Required|
|:---|:---|:---|:---|
|SourceName|Name of the metrics source. `_sourceName` can be used to search metrics from this source.|String|False|
|HostName|Name of metrics host. `_hostName` can be used to search metrics from this host.|String|False|
|SourceCategory|Category of the collected metrics. `_sourceCategory` can be used to search metrics from this category.|String|False|
|Dimensions|Key value pairs that contribute to identifying a metric. Collectd data have intrinsic dimensions with keys as `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `ds_name`, `ds_type`. The Additional dimensions specified here can help separating metrics collected from this collectd instance with metircs collected from other collectd instances.|Srings in the format of `key1` `val1` `key2` `val2` ... |False|
|Metadata|Key value pairs that do not contribute to identifying a metric. Metadata are primarily used to assist in searching metrics. Collectd data may have internal metadata. The additional metadata specified here can be used to enrich the existing metadata set.|Srings in the format of `key1` `val1` `key2` `val2` ...|False|

#### Advanced parameters
The parameters below are for advanced users. They have reasonal defaults. Normal users do not have to update these values.  

|Name|Description|Type|Default|Unit|
|:---|:---|:---|:---|:---|
|MaxBatchSize|Sumo Logic collectd output plugin batches metrics before sending them through https. MaxBatchSize defines the upper limit of metrics per batch.|Positive Integer|100|
|MaxBatchInterval|Sumo Logic collectd output plugin batches metrics before sending them through https. MaxBatchInterval defines the upper limit of duration to construct a batch.|Integer|1|Second|
|HttpPostInterval|Sumo Logic collectd output plugin schedules https post requests at fixed intervals. HttpPostInterval defines the frequency for the scheduler to run. If no metrics batch is available at the time, the sceduler immediately returns. If multiple metrics batches are available, then the oldest batch is picked to be sent.|Float|0.1|Second|
|MaxRequestsToBuffer|Sumo Logic collectd output plugin buffers failed and delayed metrics batch requests. MaxRequestsToBuffer specifies the maximum number of these requests to buffer. After the buffer becomes full, the request with oldest metrics batch will be dropped to make space for new metrics batch.|Integer|1000000|NA|
|RetryInitialDelay|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryInitialDelay specifies the initial delay before a retry is scheduled. More information can be found in the [retry library](https://pypi.python.org/pypi/retry) |Integer|0|Second|
|RetryMaxAttempts|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryMaxAttempts specifies the upper limit of retries before the current retry logic fails. Then the metric batch either is put back for the next run (when metrics buffer specified by MaxRequestsToBuffer is not full), or dropped (when metrics buffer is full). More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Integer|10|NA|
|RetryMaxDelay|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryMaxDelay specifies the upper limit of delay before the current retry logic fails. Then the metric batch either is put back for the next run (when metrics buffer specified by MaxRequestsToBuffer is not full), or dropped (when metrics buffer is full). More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Integer|100|Second|
|RetryBackOff|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryBackOff specifies the multiplier applied to delay between attempts. More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Integer|2|NA|
|RetryJitterMin|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryJitterMin specifies the minimum extra seconds added to delay between attempts. More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Integer|0|Second|
|RetryJitterMax|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryJitterMax specifies the maximum extra seconds added to delay between attempts. More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Integer|10|Second|

#### Example configuration

#### Restrictions

### 4. Start sending metrics

### 5. View metrics in Sumo Logic web app

### Furthermore
