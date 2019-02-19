#encoding=utf-8
import sys
import json

from aliyunsdkcore.acs_exception.exceptions import ServerException, ClientException
from sdk_lib.consts import *
from aliyunsdkslb.request.v20140515 import UploadServerCertificateRequest
from aliyunsdkslb.request.v20140515 import CreateLoadBalancerHTTPSListenerRequest
from aliyunsdkslb.request.v20140515 import SetLoadBalancerHTTPSListenerAttributeRequest
from sdk_lib.exception import ExceptionHandler
from sdk_lib.sdk_load_balancer import LoadBalancer
from sdk_lib.common_util import CommonUtil

client = ACS_CLIENT

'''
创建slb实例->上传服务器证书->创建https监听->上传新的服务器证书
->循环修改https监听配置
'''

def upload_server_certificate(params):
    '''
    upload_server_certificate：上传服务器证书
    官网API参考链接: https://help.aliyun.com/document_detail/34181.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = UploadServerCertificateRequest.UploadServerCertificateRequest()
            #要上传的公钥证书
            request.set_ServerCertificate(params["server_certificate"])
            #需要上传的私钥
            request.set_PrivateKey(params["private_key"])
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1

def create_https_listener(params):
    '''
    create_https_listener：创建HTTPS监听
    官网API参考链接: https://help.aliyun.com/document_detail/27593.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = CreateLoadBalancerHTTPSListenerRequest.CreateLoadBalancerHTTPSListenerRequest()
            #负载均衡实例的ID
            request.set_LoadBalancerId(params["load_balancer_id"])
            #监听的带宽峰值
            request.set_Bandwidth(params["bandwidth"])
            #负载均衡实例前端使用的端口
            request.set_ListenerPort(params["listener_port"])
            #是否开启健康检查
            request.set_HealthCheck(params["health_check"])
            #是否开启会话保持
            request.set_StickySession(params["sticky_session"])
            #负载均衡实例后端使用的端口
            request.set_BackendServerPort(params["backend_server_port"])
            #服务器证书的ID
            request.set_ServerCertificateId(params["server_certificate_id"])
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            return response_json
        except ServerException as e:
            ExceptionHandler.server_exception(e)
        except ClientException as e:
            ExceptionHandler.client_exception(e)
        finally:
            counter += 1

def set_https_listener_attribute(params):
    '''
    set_https_listener_attribute：修改HTTPS监听的配置
    官网API参考链接: https://help.aliyun.com/document_detail/27603.html
    '''
    counter = 0
    while counter < TRY_TIME:
        try:
            request = SetLoadBalancerHTTPSListenerAttributeRequest.SetLoadBalancerHTTPSListenerAttributeRequest()
            #负载均衡实例的ID
            request.set_LoadBalancerId(params["load_balancer_id"])
            #监听的带宽峰值
            request.set_Bandwidth(params["bandwidth"])
            #负载均衡实例前端使用的端口
            request.set_ListenerPort(params["listener_port"])
            #是否开启健康检查
            request.set_HealthCheck(params["health_check"])
            #是否开启会话保持
            request.set_StickySession(params["sticky_session"])
            #服务器证书的ID
            request.set_ServerCertificateId(params["server_certificate_id"])
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
    params["server_certificate"] = SERVER_CERTIFICATE
    params["private_key"] = PRIVATE_KEY
    params["health_check"] = "off"
    params["bandwidth"] = BANDWIDTH_NOT_LIMITED
    params["listener_port"] = "80"
    params["backend_server_port"] = 443
    params["sticky_session"] = "off"

    load_balancer = LoadBalancer(client)

    #创建slb实例
    load_balancer_json = load_balancer.create_load_balancer()
    params["load_balancer_id"] = load_balancer_json["LoadBalancerId"]
    CommonUtil.log("create_load_balancer", load_balancer_json)

    #上传服务器证书
    result_json = upload_server_certificate(params)
    CommonUtil.log("upload_server_certificate", result_json)
    params["server_certificate_id"] = result_json["ServerCertificateId"]

    #创建https监听
    result_json = create_https_listener(params)
    CommonUtil.log("create_https_listener", result_json)

    #上传新的服务器证书
    result_json = upload_server_certificate(params)
    CommonUtil.log("upload_server_certificate", result_json)

    #循环修改https监听配置
    result_json = set_https_listener_attribute(params)
    CommonUtil.log("set_https_listener_attribute", result_json)

    #删除slb实例
    result_json = load_balancer.delete_load_balancer(params)
    CommonUtil.log("delete_load_balancer", result_json)


if __name__ == "__main__":
    sys.exit(main())