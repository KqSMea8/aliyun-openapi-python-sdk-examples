#encoding=utf-8
import sys
import json

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from sdk_lib.consts import *
from sdk_lib.exception import ExceptionHandler
from sdk_lib.sdk_load_balancer import LoadBalancer
from sdk_lib.sdk_tcp_listener import TcpListener
from aliyunsdkslb.request.v20140515 import AddBackendServersRequest
from aliyunsdkcms.request.v20180308 import QueryMetricLastRequest
from aliyunsdkcms.request.v20180308 import CreateAlarmRequest
from sdk_lib.common_util import CommonUtil

client = ACS_CLIENT

'''
创建slb实例->创建tcp监听->创建后端服务器->
查询slb实例端口当前并发连接数->创建告警规则
'''

def add_backend_servers(params):
    '''
    add_backend_servers：添加后端服务器
    官网API参考链接: https://help.aliyun.com/document_detail/27632.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = AddBackendServersRequest.AddBackendServersRequest()
            #负载均衡实例的ID
            request.set_LoadBalancerId(params["load_balancer_id"])
            #要添加的后端服务器列表
            request.set_BackendServers(params["backend_servers"])
            response = client.do_action_with_exception(request)

            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1

def query_metric_last(params):
    '''
    query_metric_last：查询指定监控对象的最新监控数据
    官网API参考链接: https://help.aliyun.com/document_detail/51939.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = QueryMetricLastRequest.QueryMetricLastRequest()
            #名字空间，表明监控数据所属产品
            request.set_Project(params["project"])
            #监控项名称
            request.set_Metric(params["metric_name"])
            #过滤项
            request.set_Dimensions(params['dimensions'])
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1

def create_alarm(params):
    '''
    create_alarm：创建报警规则，可以为某一个实例创建报警规则，也可以为多个实例同时创建报警规则
    官网API参考链接: https://help.aliyun.com/document_detail/51910.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = CreateAlarmRequest.CreateAlarmRequest()

            #产品名称，参考各产品对应的project
            request.set_Namespace(params["name_space"])
            #报警规则名称
            request.set_Name(params["name"])
            #相应产品对应的监控项名称，参考各产品metric定义
            request.set_MetricName(params["metric_name"])
            #报警规则对应实例列表
            request.set_Dimensions(params["dimensions"])
            #统计方法，必须与定义的metric一致
            request.set_Statistics(params["statistics"])
            #报警比较符
            request.set_ComparisonOperator(params["comparison_operator"])
            #报警阈值，目前只开放数值类型功能
            request.set_Threshold(params["threshold"])
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1

def main():

    params = {}
    params["backend_servers"] = [{"ServerId": ECS_INSTANCE_ID, "Weight": "100"}]
    params["bandwidth"] = BANDWIDTH_NOT_LIMITED
    params["listener_port"] = 443
    params["backend_server_port"] = 443
    params["project"] = "acs_slb_dashboard"
    params["traffic_tx_new"] = "TrafficTXNew"
    params["name_space"] = "acs_slb_dashboard"
    params["name"] = "slb_alarm"
    params["metric_name"] = "TrafficTXNew"
    params["statistics"] = "Average"
    params["comparison_operator"] = "<="
    params["threshold"] = 35

    load_balancer = LoadBalancer(client)
    tcp_listener = TcpListener(client)

    #创建slb实例
    load_balancer_json = load_balancer.create_load_balancer()
    CommonUtil.log("create_load_balancer", load_balancer_json)

    #slb实例id
    params["load_balancer_id"] = load_balancer_json["LoadBalancerId"]

    #创建tcp监听
    result_json = tcp_listener.create_tcp_listener(params)
    CommonUtil.log("create_tcp_listener", result_json)

    #创建后端服务器
    result_json = add_backend_servers(params)
    CommonUtil.log("add_backend_servers", result_json)

    #查询slb实例端口当前并发连接数
    params["metric_name"] = "MaxConnection"
    params["dimensions"] = '[{"instanceId":"' + load_balancer_json["LoadBalancerId"] + '"}]'
    result_json = query_metric_last(params)
    CommonUtil.log("query_metric_last", result_json)

    #创建告警规则
    params["metric_name"] = "TrafficTXNew"
    result_json = create_alarm(params)
    CommonUtil.log("create_alarm", result_json)

    #删除slb实例
    result_json = load_balancer.delete_load_balancer(params)
    CommonUtil.log("delete_load_balancer", result_json)

if __name__ == "__main__":
    sys.exit(main())