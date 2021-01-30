from flask import (
    jsonify,
    Blueprint,
    request
)
from onecomic.comicbook import ComicBook

from .common import crawler
from . import config


app = Blueprint("index", __name__, url_prefix='/',)


@app.route("/")
def index():
    prefix = config.URL_PREFIX
    q_site = request.args.get('site')
    api_examples = []
    for item in crawler.get_all_cralwer_config():
        item['examples'] = []
        if not q_site:
            api_examples.append(item)
        elif item['site'] == q_site:
            api_examples.append(item)
    for item in api_examples:
        site = item['site']
        site_examples = item['examples']
        comicid = ComicBook.CRAWLER_CLS_MAP[site].DEFAULT_COMICID
        search_name = ComicBook.CRAWLER_CLS_MAP[site].DEFAULT_SEARCH_NAME
        tag = ComicBook.CRAWLER_CLS_MAP[site].DEFAULT_TAG

        site_examples.append(dict(
            desc='根据漫画id 获取漫画信息',
            api=prefix + f'/api/{site}/comic/{comicid}'
        ))

        # 章节详情
        site_examples.append(dict(
            desc='获取章节信息',
            api=prefix + f'/api/{site}/comic/{comicid}/1'
        ))

        # 搜索
        site_examples.append(dict(
            desc='搜索',
            api=prefix + f'/api/{site}/search?name={search_name}&page=1'
        ))

        # 最近更新
        site_examples.append(dict(
            desc="查看站点最近更新",
            api=prefix + f'/api/{site}/latest?page=1'
        ))

        # 查看所有tags
        site_examples.append(dict(
            desc="获取站点所有tags",
            api=prefix + f'/api/{site}/tags'
        ))

        # 根据tag查询
        site_examples.append(dict(
            desc="根据tag查询",
            api=prefix + f'/api/{site}/list?tag={tag}&page=1'
        ))

    aggregate_examples = []
    aggregate_examples.append(dict(
        desc="聚合搜索",
        api=prefix + '/aggregate/search?name=海贼&site=bilibili,u17'
    ))

    tools_examples = []
    tools_examples.append(dict(
        desc="聚合搜索",
        api=prefix + '/tools/urlinfo?url=https://www.u17.com/comic/53210.html'
    ))

    manage_examples = []
    manage_examples.append(dict(
        desc='添加任务',
        api=prefix + '/manage/task/add?site=qq&comicid=505430&chapter=-1&gen_pdf=1&send_mail=0',
    ))
    manage_examples.append(dict(
        desc='查看任务',
        api=prefix + '/manage/task/list?page=1',
    ))
    # GET获取/POST更新站点cookies
    manage_examples.append(dict(
        desc='GET获取/POST更新站点cookies',
        api=prefix + f'/manage/cookies/qq',
    ))
    # 查看/设置站点代理
    manage_examples.append(dict(
        desc='查看/设置站点代理',
        api=prefix + f'/manage/proxy/qq',
    ))

    return jsonify(
        {
            "api_examples": api_examples,
            "aggregate_examples": aggregate_examples,
            "tools_examples": tools_examples,
            "manage_examples": manage_examples,
        }
    )


@app.route("/crawler/config")
def crawler_config():
    return jsonify(
        {
            'configs': crawler.get_all_cralwer_config()
        }
    )
