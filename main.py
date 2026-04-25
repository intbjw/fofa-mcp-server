# -*- coding: utf-8 -*-
import base64
import os
from typing import Any, Dict
import httpx
from mcp.server.fastmcp import FastMCP

# FOFA API 配置
FOFA_KEY = os.getenv("FOFA_KEY")
FOFA_API_URL = "https://fofa.info/api/v1"
# 需要查询的字段
FOFA_FIELDS_ALL = "ip,port,protocol,country,country_name,region,city,longitude,latitude,as_number,as_organization,host,domain,os,server,icp,title,jarm,header,banner,base_protocol,link,certs_issuer_org,certs_issuer_cn,certs_subject_org,certs_subject_cn,tls_ja3s,tls_version,product,product_category,version,lastupdatetime,cname"

FOFA_FIELDS = "ip,port,protocol,host,domain,icp,title,product,version,lastupdatetime"
# 初始化 MCP Server
mcp = FastMCP("FOFA-MCP-Server")
request_session = httpx.AsyncClient()


# FOFA API 查询封装


async def fofa_search(query: str, fields: str, size: int = 50) -> dict[str, Any] | None:
    """执行 FOFA 查询"""
    query_base64 = base64.b64encode(query.encode()).decode()
    if fields == 'all':
        fields = FOFA_FIELDS_ALL
    else:
        fields = FOFA_FIELDS
    params = {
        "key": FOFA_KEY,
        "qbase64": query_base64,
        "size": size,
        "fields": fields
    }
    headers = {"Accept-Encoding": "gzip"}
    URL = f"{FOFA_API_URL}/search/all"
    try:
        response = await request_session.get(URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(data)
        if data:
            if data.get("error"):
                data["results"] = [
                    dict(zip(FOFA_FIELDS.split(","), item))
                    for item in data["results"]
                ]
            return data
        return None
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    return None


def format_info(data: dict[str, Any], fields: str) -> dict[str, Any]:
    """格式化查询结果"""
    if not data:
        return {"summary": "未找到结果", "data": []}
    formatted = {}
    formatted["data"] = []
    # 添加查询统计信息
    summary = [
        f"查询状态: {'成功' if not data.get('error', True) else '失败'}",
        f"消耗点数: {data.get('consumed_fpoint', 0)}",
        f"所需点数: {data.get('required_fpoints', 0)}",
        f"结果总数: {data.get('size', 0)}",
        f"当前页数: {data.get('page', 1)}",
        f"查询模式: {data.get('mode', 'extended')}",
        f"查询语句: {data.get('query', '')}"
    ]
    formatted["summary"] = "\n".join(summary)
    if data.get('error'):
        return {"summary": "\n".join(summary) + f"\n错误提示: {data.get('errmsg', '未知错误')}", "data": []}

    if not data.get('results'):
        return {"summary": "\n".join(summary) + "\n未找到匹配结果", "data": []}

    result = data.get('results')

    for item in result:
        if fields == 'all':
            info = {
                "IP": item[0],
                "端口": item[1],
                "协议": item[2],
                "国家代码": item[3],
                "国家名": item[4],
                "地区": item[5],
                "城市": item[6],
                "经度": item[7],
                "纬度": item[8],
                "ASN编号": item[9],
                "ASN组织": item[10],
                "主机名": item[11],
                "域名": item[12],
                "操作系统": item[13],
                "服务器": item[14],
                "ICP备案号": item[15],
                "网站标题": item[16],
                "JARM指纹": item[17],
                "Header": item[18],
                "Banner": item[19],
                "基础协议": item[20],
                "URL链接": item[21],
                "证书颁发者组织": item[22],
                "证书颁发者通用名称": item[23],
                "证书持有者组织": item[24],
                "证书持有者通用名称": item[25],
                "JA3S指纹": item[26],
                "TLS版本": item[27],
                "产品名": item[28],
                "产品分类": item[29],
                "版本号": item[30],
                "最后更新时间": item[31],
                "域名CNAME": item[32]
            }
        else:
            info = {
                "IP": item[0],
                "端口": item[1],
                "协议": item[2],
                "主机名": item[3],
                "域名": item[4],
                "ICP备案号": item[5],
                "网站标题": item[6],
                "产品名": item[7],
                "版本号": item[8],
                "最后更新时间": item[9]
            }
        formatted["data"].append(info)

    return formatted


async def fofa_userinfo() -> Any | None:
    """查询FOFA账户信息"""
    URL = f"{FOFA_API_URL}/info/my"
    params = {
        "key": FOFA_KEY
    }
    headers = {"Accept-Encoding": "gzip"}
    try:
        response = await request_session.get(URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


async def fofa_search_next(query: str, fields: str, size: int = 50, next_id: str = "", full: bool = False) -> dict[str, Any] | None:
    """基于游标的翻页查询"""
    query_base64 = base64.b64encode(query.encode()).decode()
    if fields == 'all':
        fields = FOFA_FIELDS_ALL
    else:
        fields = FOFA_FIELDS
    params = {
        "key": FOFA_KEY,
        "qbase64": query_base64,
        "fields": fields,
        "size": size,
        "full": str(full).lower(),
    }
    if next_id:
        params["next"] = next_id
    headers = {"Accept-Encoding": "gzip"}
    URL = f"{FOFA_API_URL}/search/next"
    try:
        response = await request_session.get(URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


async def fofa_search_stats(query: str, fields: str = "title,country", size: int = 5) -> dict[str, Any] | None:
    """查询搜索结果的聚合统计信息"""
    query_base64 = base64.b64encode(query.encode()).decode()
    params = {
        "key": FOFA_KEY,
        "qbase64": query_base64,
        "fields": fields,
        "size": size,
    }
    headers = {"Accept-Encoding": "gzip"}
    URL = f"{FOFA_API_URL}/search/stats"
    try:
        response = await request_session.get(URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


async def fofa_host_info(host: str, detail: bool = False) -> dict[str, Any] | None:
    """查询某个 IP 或域名的 host 聚合信息"""
    params = {
        "key": FOFA_KEY,
        "detail": str(detail).lower(),
    }
    headers = {"Accept-Encoding": "gzip"}
    URL = f"{FOFA_API_URL}/host/{host}"
    try:
        response = await request_session.get(URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


@mcp.tool()
async def fofa_search_tool(query: str, fields: str = "", size: int = 50) -> Any:
    """使用 FOFA API 进行搜索查询，返回格式化结果。

    :param query: FOFA 查询语句，例如 'title="bing"' 或 'domain="example.com"'
    :param fields: 返回字段，传 'all' 返回全部字段，留空返回默认字段
    :param size: 返回结果数量，默认 50，最大 10000
    """
    result = await fofa_search(query, fields, size)
    return format_info(result, fields) if result else None


@mcp.tool()
async def fofa_search_next_tool(query: str, fields: str = "", size: int = 50, next_id: str = "", full: bool = False) -> Any:
    """使用游标翻页方式查询 FOFA，适合大批量数据获取。

    :param query: FOFA 查询语句
    :param fields: 返回字段，传 'all' 返回全部字段，留空返回默认字段
    :param size: 每页结果数量，默认 50，最大 10000
    :param next_id: 上一次查询返回的 next 游标值，首次查询留空
    :param full: 是否搜索全量数据（默认只搜索近一年），True 表示搜索全部
    """
    result = await fofa_search_next(query, fields, size, next_id, full)
    if not result:
        return None
    # 将结果格式化，同时透传 next 游标供下次翻页使用
    formatted = format_info(result, fields)
    formatted["next"] = result.get("next", "")
    return formatted


@mcp.tool()
async def fofa_stats_tool(query: str, fields: str = "title,country", size: int = 5) -> Any:
    """查询 FOFA 搜索结果的聚合统计信息（各字段 TOP N 分布）。

    :param query: FOFA 查询语句
    :param fields: 需要聚合统计的字段，逗号分隔，例如 'title,country,port,product'
    :param size: 每个字段返回 TOP N 条，默认 5
    """
    return await fofa_search_stats(query, fields, size)


@mcp.tool()
async def fofa_host_tool(host: str, detail: bool = False) -> Any:
    """查询某个 IP 或域名的 host 聚合信息，包含端口、协议、产品等汇总数据。

    :param host: 目标 IP 或域名，例如 '8.8.8.8' 或 'example.com'
    :param detail: 是否返回详细数据，True 时包含更多字段信息
    """
    return await fofa_host_info(host, detail)


@mcp.tool()
async def fofa_userinfo_tool() -> Any:
    """查询当前 FOFA 账户信息，包括剩余 F 点、API 配额等。"""
    return await fofa_userinfo()


if __name__ == "__main__":
    # import asyncio
    # # 测试异步函数调用

    # async def test_search():
    #     result = await fofa_search_tool("YXBwPSJuZ2lueCI=", 10)
    #     print(result)

    # # 运行测试函数
    # asyncio.run(test_search())
    # 启动MCP服务器
    mcp.run(transport='stdio')
