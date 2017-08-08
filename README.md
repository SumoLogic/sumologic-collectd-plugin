# Sumo Logic Collectd Plugin

This is a plugin for [collectd](https://collectd.org/).
It is fully free and fully open source. The license is Apache 2.0, meaning you are pretty much free to use it however you want in whatever way.

## Getting Started

### 1. Install collectd on you matchine
If collected is already installed, safely skip this step. Otherwise, follow the instructions in the [collectd download](https://collectd.org/download.shtml) site for download and installation. There are some more information for getting novice users started in collectd Wiki [first_steps](https://collectd.org/wiki/index.php/First_steps) 

### 2. Install Sumo Logic collectd plugin into collectd
The Sumo Logic collectd plugin module can be anywhere in your system. Here is an example of installing this plugin into a collectd directory.
```
1. Go to collectd root dir
2. cd ./lib
3. mkdir collectd_python.plugin
4. cd collectd_python.plugin
5. git clone git@github.com:SumoLogic/sumologic-collectd-plugin.git
```
Sumo Logic collectd plugin uses [requests](http://docs.python-requests.org/en/master/) and [retry](https://pypi.python.org/pypi/retrying) libraries for sumbitting https requests. If they are not installed. Install them using pip.
```
sudo pip install requests
sudo pip install retry
```

### 3. Set up metrics http source
N/A atm

### 4. Setup Sumo Logic collectd plugin configurations
Sumo Logic collectd plugin supports following prarmeters. 

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
|Dimensions|Key value pairs that contribute to identifying a metric. Collectd data have intrinsic dimensions with keys as `host`, `plugin`, `plugin_instance`, `type`, `type_instance`, `ds_name`, `ds_type`. The Additional dimensions specified here can help separating metrics collected from this collectd instance with metircs collected from other collectd instances. Dimensions cannot contain [reserved symbols](https://github.com/CCheSumo/collectd-plugin/blob/master/README.md#reserved-symbols) and [reserved keywords](https://github.com/CCheSumo/collectd-plugin/blob/master/README.md#reserved-keywords).|Srings in the format of `key1` `val1` `key2` `val2` ... |False|
|Metadata|Key value pairs that do not contribute to identifying a metric. Metadata are primarily used to assist in searching metrics. Collectd data may have internal metadata. The additional metadata specified here can be used to enrich the existing metadata set. Metadata cannot contain [reserved symbols](https://github.com/CCheSumo/collectd-plugin/blob/master/README.md#reserved-symbols) and [reserved keywords](https://github.com/CCheSumo/collectd-plugin/blob/master/README.md#reserved-keywords)|Srings in the format of `key1` `val1` `key2` `val2` ...|False|

#### Advanced parameters
Sumo Logic collectd plugin also supports some [advanced configurations](https://github.com/CCheSumo/collectd-plugin/blob/master/README.md#advanced-parameters-1). These configurations have reasonable defaults and normally do not need to be updated. 

#### Example configuration
An exmple configuration for the plugin is shown below (code to be added to collectd.conf under $collectd_root/etc).
```
LoadPlugin python
<Plugin python>
    	ModulePath "/path/to/your/collectd_python.plugin/sumologic-collectd-plugin/src"
    	LogTraces true
    	Interactive false
    	Import "metrics_writer"
    
    	<Module "metrics_writer">
	    	TypesDB "/usr/local/Cellar/collectd/5.7.2/share/collectd/types.db"
      	    	URL "/path/to/your/http/endpoint"

	    	SourceName my_source_name
	    	HostName my_host
	    	SourceCategory my_category

	    	Dimensions my_dim_key1 my_dim_val1
	    	Metadata my_meta_key1 my_meta_val1 my_meta_key2 my_meta_key2
    	</Module>
</Plugin>
```

Other recommended modules.
It is recommeded to setup the following two plugins in collectd.conf. The functionalities of the two plugins are explained in collectd Wiki [Plugin:LogFile](https://collectd.org/wiki/index.php/Plugin:LogFile) and [Plugin:CSV](https://collectd.org/wiki/index.php/Plugin:CSV)
```
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
The following pulgins, if enabled in collectd.conf, enables collecting [cpu](https://collectd.org/wiki/index.php/Plugin:CPU), [memory](https://collectd.org/wiki/index.php/Plugin:Memory), [disk](https://collectd.org/wiki/index.php/Plugin:Disk), [network](https://collectd.org/wiki/index.php/Plugin:Interface) metrics from the system. 
```
LoadPlugin cpu
LoadPlugin memory
LoadPlugin disk
LoadPlugin interface
```
A list of all collectd plugins is awailable in collectd Wiki [Table of Plugins](https://collectd.org/wiki/index.php/Table_of_Plugins)

#### Reserved symbols
Equal sign and space are reserved symbols.
```
"=", " "
```
#### Reserved keywords
Following terms are reserved for Sumo Logic internal use only.
```
"_sourcehost", "_sourcename", "_sourcecategory", "_collectorid", "_collector", "_source", "_sourceid", "_contenttype", "_rawname"
```

### 5. Start sending metrics
Start sending metrics by simply running collectd, e.g. (command can be differnt depends on collectd installation)
```
 sudo /usr/local/sbin/collectd -f -C /usr/local/etc/collectd.conf
 
```

#### View logs
If logfile is installed, then you can view logs by tailling collectd.log file, e.g. (command can be differnt depends on collectd installation)
```
tail -f /var/log/collectd.log
```

#### Data model
Metrics sending out by Sumo Logic collectd plugin is in [Carbon 2.0](https://gowalker.org/github.com/metrics20/go-metrics20/carbon20) format, where a metrics is defined as:
```
dimensions  metadata value timestamp
```
`dimensions` and `metadata` are key/value pairs of strings. `dimensions` contributes to uniquely identifying a metric. `metadata` do not contribute to identifying a metric. They are used to categorize metrics for searching. 
`value` is a double number
`timestamp` is a long number

Example data before compression 
```
host=my_mac plugin=cpu plugin_instance=1 type=cpu type_instance=user ds_name=value ds_type=DERIVE  meta_key1=meta_val1 5991.000000 1502148249
host=my_mac plugin=cpu plugin_instance=0 type=cpu type_instance=user ds_name=value ds_type=DERIVE  meta_key1=meta_val1 98722.000000 1502148249
```

#### Compression
Metrics after batching are compressed before being sent. The compression algorithm is `deflate`. The algorithm is explained in more details in [An Explanation of the Deflate Algorithm](https://zlib.net/feldspar.html)

#### Error handling
Sumo Logic collectd plugin retries failed https requests if the exception is recoverable. If the exception is unrecoverable, it will simply abort. Several client side errors and most server side errors are treated as recoverable exceptions. 
A complete set of Http status code is available here [List of HTTP status codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes). 

The status codes recognized as recoverable exceptions in Sumo Logic collectd plugin are provided below:

##### Client side recoverable exceptions
Error codes: 404, 408, 429

##### Server side recoverable exceptions
Error codes: 500, 502, 503, 504, 506, 507, 508, 510, 511

#### Retry failure and buffering
Sumo Logic collectd plugin retries on recoverable exceptions by default. When all retries fail, the request is either put back to scheudle for next run, or dropped, based on the buffer status. By default, 1000000 requests are buffered. If the buffer becomes full, then requests failed after all retries will be dropped. Otherwise, it is put back to the processing queue for the next run.

### 6. View metrics in Sumo Logic web app

## Advanced Topics

### 1. Advanced parameters
The parameters below are for advanced users. They have reasonal defaults. Normal users do not have to update these values.  

|Name|Description|Type|Default|Unit|
|:---|:---|:---|:---|:---|
|MaxBatchSize|Sumo Logic collectd output plugin batches metrics before sending them through https. MaxBatchSize defines the upper limit of metrics per batch.|Positive Integer|5000|
|MaxBatchInterval|Sumo Logic collectd output plugin batches metrics before sending them through https. MaxBatchInterval defines the upper limit of duration to construct a batch.|Positive Integer|1|Second|
|HttpPostInterval|Sumo Logic collectd output plugin schedules https post requests at fixed intervals. HttpPostInterval defines the frequency for the scheduler to run. If no metrics batch is available at the time, the sceduler immediately returns. If multiple metrics batches are available, then the oldest batch is picked to be sent.|Positive Float|0.1|Second|
|MaxRequestsToBuffer|Sumo Logic collectd output plugin buffers failed and delayed metrics batch requests. MaxRequestsToBuffer specifies the maximum number of these requests to buffer. After the buffer becomes full, the request with oldest metrics batch will be dropped to make space for new metrics batch.|Positive Integer|1000000|NA|
|RetryInitialDelay|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryInitialDelay specifies the initial delay before a retry is scheduled. More information can be found in the [retry library](https://pypi.python.org/pypi/retry) |Non-negative Integer|0|Second|
|RetryMaxAttempts|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryMaxAttempts specifies the upper limit of retries before the current retry logic fails. Then the metric batch either is put back for the next run (when metrics buffer specified by MaxRequestsToBuffer is not full), or dropped (when metrics buffer is full). More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Positive Integer|10|NA|
|RetryMaxDelay|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryMaxDelay specifies the upper limit of delay before the current retry logic fails. Then the metric batch either is put back for the next run (when metrics buffer specified by MaxRequestsToBuffer is not full), or dropped (when metrics buffer is full). More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Positive Integer|100|Second|
|RetryBackOff|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryBackOff specifies the multiplier applied to delay between attempts. More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Positive Integer|2|NA|
|RetryJitterMin|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryJitterMin specifies the minimum extra seconds added to delay between attempts. More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Non-negative Integer|0|Second|
|RetryJitterMax|Sumo Logic collectd output plugin retries on recoverable exceptions. RetryJitterMax specifies the maximum extra seconds added to delay between attempts. More information can be found in the [retry library](https://pypi.python.org/pypi/retry)|Non-negative Integer|10|Second|
