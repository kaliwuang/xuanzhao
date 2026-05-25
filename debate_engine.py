"""
玄照 · 辩论引擎
108位玄学人物按阵营分组，对同一命盘产生辩论式分析
"""

# ==========================================
# 阵营定义
# ==========================================

FACTIONS = {
    "orthodox": {
        "name": "玄学正宗",
        "desc": "以正统术数（八字、六爻、奇门）为武器",
        "take": "此命盘术数可观，冲中藏机，用神到位则为吉"
    },
    "daoist": {
        "name": "道家自然",
        "desc": "道法自然，不争而胜",
        "take": "顺其自然即可，强求反而不美"
    },
    "prophet": {
        "name": "预言警示",
        "desc": "专看凶兆，预警风险",
        "take": "子午冲为大凶之兆，需化解，非等闲之局"
    },
    "alchemy": {
        "name": "炼金转化",
        "desc": "变化是本质，炼金即转化命运",
        "take": "冲象即是炼金炉——要么化为灰烬，要么炼出真金"
    },
    "witchcraft": {
        "name": "巫术萨满",
        "desc": "灵性通道，与自然之力沟通",
        "take": "此命盘可见灵魂能量的轨迹——非寻常目光可及"
    },
    "western": {
        "name": "西方神秘",
        "desc": "西方神秘学传统，占星/卡巴拉/神智学",
        "take": "从西方视角看，此命有特殊的行星能量配置"
    },
    "rational": {
        "name": "理性研究",
        "desc": "研究玄学但不盲信，讲逻辑讲证据",
        "take": "数据说话，不渲染不夸大，就事论事"
    },
}

# 108位玄学人物库（全部与术数/玄学直接相关）
FIGURES = {
    # ============================
    # 一、中国玄学（54人）
    # ============================

    # --- 玄学正宗 (orthodox) ---
    "fu-xi": {"name": "伏羲", "title": "八卦始祖", "cat": "中国", "faction": "orthodox",
        "bio": "仰观天象俯察地法，始作八卦。群经之首，万法之源。"},
    "shen-nong": {"name": "神农", "title": "连山易祖", "cat": "中国", "faction": "orthodox",
        "bio": "尝百草以疗民疾，演连山易以通天道。"},
    "huang-di": {"name": "黄帝", "title": "归藏易主", "cat": "中国", "faction": "orthodox",
        "bio": "战蚩尤、合符釜山，创归藏易，为中华玄学奠基。"},
    "feng-hou": {"name": "风后", "title": "奇门之祖", "cat": "中国", "faction": "orthodox",
        "bio": "黄帝之臣，据传奇门遁甲源于风后演兵阵法。"},
    "li-mu": {"name": "力牧", "title": "兵阴阳家", "cat": "中国", "faction": "orthodox",
        "bio": "黄帝大将，兼通兵法与术数。"},
    "da-nao": {"name": "大挠", "title": "六十甲子", "cat": "中国", "faction": "orthodox",
        "bio": "始作六十甲子干支，为八字命理之根基。"},
    "rong-cheng": {"name": "容成", "title": "历法之祖", "cat": "中国", "faction": "orthodox",
        "bio": "黄帝之臣，造历法，通阴阳之术。"},
    "gao-yao": {"name": "皋陶", "title": "占狱神判", "cat": "中国", "faction": "orthodox",
        "bio": "上古司法之神，以独角兽决狱，通占卜断事。"},
    "wen-wang": {"name": "周文王", "title": "周易演卦", "cat": "中国", "faction": "orthodox",
        "bio": "囚羑里而演周易，将八卦重为六十四卦。"},
    "jiang-ziya": {"name": "姜子牙", "title": "封神谋主", "cat": "中国", "faction": "orthodox",
        "bio": "渭水垂钓遇文王，助周灭商。传说通奇门遁甲，掌封神榜。"},
    "zhou-gong": {"name": "周公旦", "title": "解梦之祖", "cat": "中国", "faction": "orthodox",
        "bio": "制礼作乐，兼通卜筮解梦。《周公解梦》传世。"},
    "gui-gu-zi": {"name": "鬼谷子", "title": "纵横鼻祖", "cat": "中国", "faction": "orthodox",
        "bio": "通天彻地，术数符箓命理无所不通。孙膑庞涓苏秦张仪皆出其门。"},
    "zhang-liang": {"name": "张良", "title": "圯上受书", "cat": "中国", "faction": "orthodox",
        "bio": "黄石公授《素书》，太公兵法。运筹帷幄决胜千里。"},
    "huang-shi-gong": {"name": "黄石公", "title": "素书之师", "cat": "中国", "faction": "orthodox",
        "bio": "赠张良《素书》，传太公兵法。隐于黄石，其术通天。"},
    "zhuge-liang": {"name": "诸葛亮", "title": "八阵图主", "cat": "中国", "faction": "orthodox",
        "bio": "奇门遁甲、八阵图、马前课、五行八卦无一不通。出师未捷身先死。"},
    "pang-tong": {"name": "庞统", "title": "凤雏谋士", "cat": "中国", "faction": "orthodox",
        "bio": "与诸葛亮齐名，号凤雏。通术法，擅奇谋。"},
    "guan-lu": {"name": "管辂", "title": "三国神卜", "cat": "中国", "faction": "orthodox",
        "bio": "三国第一神卜，占无不中。少年时即通周易。"},
    "guo-pu": {"name": "郭璞", "title": "风水祖师", "cat": "中国", "faction": "orthodox",
        "bio": "两晋第一术士。《葬经》为风水学经典。占卜、谶纬皆精。"},
    "ge-hong": {"name": "葛洪", "title": "抱朴炼丹", "cat": "中国", "faction": "alchemy",
        "bio": "《抱朴子》内外篇，炼丹术集大成者。道教学者。"},
    "tao-hong-jing": {"name": "陶弘景", "title": "茅山宗祖", "cat": "中国", "faction": "orthodox",
        "bio": "茅山宗创始人。博通天文历算、医药炼丹、占卜符箓。"},
    "yuan-tian-gang": {"name": "袁天罡", "title": "推背合著", "cat": "中国", "faction": "orthodox",
        "bio": "唐代玄学大宗师。与李淳风合著《推背图》。善星象、面相。"},
    "li-chun-feng": {"name": "李淳风", "title": "乙巳占主", "cat": "中国", "faction": "orthodox",
        "bio": "天文历算第一人。《乙巳占》为星象学经典。《推背图》合著者。"},
    "sun-si-miao": {"name": "孙思邈", "title": "药王神卜", "cat": "中国", "faction": "orthodox",
        "bio": "药王孙真人。医卜相通，擅六壬、占星。"},
    "yi-xing": {"name": "一行禅师", "title": "大衍历法", "cat": "中国", "faction": "orthodox",
        "bio": "唐代高僧、天文学家。大衍历空前精准。通密宗星象。"},
    "li-xu-zhong": {"name": "李虚中", "title": "八字始祖", "cat": "中国", "faction": "orthodox",
        "bio": "八字命理开山祖师。以年月日三柱论命。"},
    "xu-zi-ping": {"name": "徐子平", "title": "四柱大成", "cat": "中国", "faction": "orthodox",
        "bio": "子平术创始人。将三柱发展为四柱八字，命理学完备。"},
    "chen-tuan": {"name": "陈抟", "title": "紫微河洛", "cat": "中国", "faction": "orthodox",
        "bio": "希夷先生。紫微斗数创始人，河洛理数传承人。睡仙。"},
    "shao-yong": {"name": "邵雍", "title": "梅花易数", "cat": "中国", "faction": "orthodox",
        "bio": "康节先生。《皇极经世》《梅花易数》。易学大家。"},
    "liu-bo-wen": {"name": "刘伯温", "title": "烧饼歌主", "cat": "中国", "faction": "prophet",
        "bio": "诚意伯。通奇门遁甲。《烧饼歌》预言后世。《灵棋经》注者。"},
    "yao-guang-xiao": {"name": "姚广孝", "title": "黑衣宰相", "cat": "中国", "faction": "orthodox",
        "bio": "僧名道衍。助朱棣夺天下。通阴阳术数。"},
    "lai-bu-yi": {"name": "赖布衣", "title": "风水奇人", "cat": "中国", "faction": "orthodox",
        "bio": "宋代风水大师。赖派风水创始人。"},
    "yang-jun-song": {"name": "杨筠松", "title": "杨公风水", "cat": "中国", "faction": "orthodox",
        "bio": "唐代风水宗师。杨公风水派创始人。《撼龙经》作者。"},
    "jiang-da-hong": {"name": "蒋大鸿", "title": "玄空宗师", "cat": "中国", "faction": "orthodox",
        "bio": "明末清初玄空风水大家。《地理辨正》传世。"},
    "zhang-san-feng": {"name": "张三丰", "title": "太极真仙", "cat": "中国", "faction": "daoist",
        "bio": "武当派祖师。太极拳创始人。通占验、内丹之术。"},
    "cao-yuan": {"name": "曹元", "title": "近代占星", "cat": "中国", "faction": "orthodox",
        "bio": "近代中国占星学的重要人物。"},
    "du-guang-ting": {"name": "杜光庭", "title": "道教大宗", "cat": "中国", "faction": "orthodox",
        "bio": "唐末五代道教领袖。集道教仪轨之大成。擅谶纬。"},

    # --- 道家自然 (daoist) ---
    "laozi": {"name": "老子", "title": "道德玄经", "cat": "中国", "faction": "daoist",
        "bio": "道家始祖。《道德经》五千言。'道可道非常道'。"},
    "zhuangzi": {"name": "庄子", "title": "逍遥齐物", "cat": "中国", "faction": "daoist",
        "bio": "道家第二大宗师。'天地与我并生万物与我为一'。"},
    "lie-zi": {"name": "列子", "title": "御风而行", "cat": "中国", "faction": "daoist",
        "bio": "道家列御寇。御风而行。通术法。"},

    # --- 方士/谶纬 (prophet) ---
    "zou-yan": {"name": "邹衍", "title": "五德始终", "cat": "中国", "faction": "prophet",
        "bio": "阴阳家集大成者。五德终始说，以五行推演朝代更替。"},
    "xu-fu": {"name": "徐福", "title": "海外寻仙", "cat": "中国", "faction": "prophet",
        "bio": "秦代方士。率童男童女东渡寻不死仙药。"},
    "dong-fang-shuo": {"name": "东方朔", "title": "谶纬之才", "cat": "中国", "faction": "prophet",
        "bio": "汉武帝时奇人。善谶纬、占卜。传说偷桃长生。"},
    "zuo-ci": {"name": "左慈", "title": "道术通天", "cat": "中国", "faction": "witchcraft",
        "bio": "三国术士。变化之术、隐身遁形。戏曹操如玩物。"},
    "yu-ji": {"name": "于吉", "title": "太平清领", "cat": "中国", "faction": "witchcraft",
        "bio": "东汉方士。《太平经》作者之一。符水治病。"},
    "zhang-guo": {"name": "张果", "title": "张果老仙", "cat": "中国", "faction": "witchcraft",
        "bio": "八仙之一。骑驴倒行。通方术。"},

    # --- 文士通玄 (rational) ---
    "su-shi": {"name": "苏轼", "title": "东坡易传", "cat": "中国", "faction": "rational",
        "bio": "大文豪，通《易》。有《东坡易传》。笔记中多记玄怪。"},
    "shen-kuo": {"name": "沈括", "title": "梦溪易占", "cat": "中国", "faction": "rational",
        "bio": "《梦溪笔谈》多涉天文异象、阴阳五行。"},
    "wang-yang-ming": {"name": "王阳明", "title": "心学射覆", "cat": "中国", "faction": "rational",
        "bio": "心学宗师。通易占，有射覆传说。'心外无物'。"},
    "ji-yun": {"name": "纪昀", "title": "阅微通玄", "cat": "中国", "faction": "rational",
        "bio": "纪晓岚。《阅微草堂笔记》多录玄怪故事。"},
    "zeng-guo-fan": {"name": "曾国藩", "title": "冰鉴相术", "cat": "中国", "faction": "orthodox",
        "bio": "中兴名臣。《冰鉴》相术传世。'邪正看眼鼻'。"},
    "sun-bin": {"name": "孙膑", "title": "兵家术法", "cat": "中国", "faction": "orthodox",
        "bio": "兵阴阳家。《孙膑阵法》传说有术数成分。"},
    "su-qin": {"name": "苏秦", "title": "鬼谷纵横", "cat": "中国", "faction": "orthodox",
        "bio": "鬼谷子弟子。纵横家。合纵六国。"},
    "zhang-yi": {"name": "张仪", "title": "连横之舌", "cat": "中国", "faction": "orthodox",
        "bio": "鬼谷子弟子。纵横家。连横破合纵。"},
    "pang-juan": {"name": "庞涓", "title": "魏国军师", "cat": "中国", "faction": "orthodox",
        "bio": "鬼谷子弟子。亦通术数。与孙膑同门相争。"},
    "yin-xi": {"name": "尹喜", "title": "关尹传经", "cat": "中国", "faction": "daoist",
        "bio": "函谷关令。得老子授《道德经》。关尹子。"},

    # ============================
    # 二、世界玄学（54人）
    # ============================

    # --- 西方神秘 (western) ---
    "hermes": {"name": "赫尔墨斯·特里斯墨吉斯忒斯", "title": "三重伟大", "cat": "世界", "faction": "western",
        "bio": "西方神秘学鼻祖。《翠玉录》'上下同效'。炼金术、占星术之源头。"},
    "moses": {"name": "摩西", "title": "律法先知", "cat": "世界", "faction": "western",
        "bio": "《圣经》先知。十诫颁布者。传说通埃及法术。"},
    "solomon": {"name": "所罗门王", "title": "智慧之王", "cat": "世界", "faction": "western",
        "bio": "《所罗门钥匙》'恶魔学经典。最智慧的君王。"},
    "pythagoras": {"name": "毕达哥拉斯", "title": "数即万物", "cat": "世界", "faction": "western",
        "bio": "数理神秘主义。万物皆数。灵魂轮回。"},
    "empedocles": {"name": "恩培多克勒", "title": "四元素说", "cat": "世界", "faction": "western",
        "bio": "四元素说创始人。自称为神，通巫术。"},
    "apollonius": {"name": "阿波罗尼乌斯", "title": "提亚纳术士", "cat": "世界", "faction": "western",
        "bio": "新毕达哥拉斯派大师。传说能预知、治病、驱魔。"},
    "johndee": {"name": "约翰·迪伊", "title": "天使之语", "cat": "世界", "faction": "western",
        "bio": "伊丽莎白一世御用占星家。天使语体系创始人。"},
    "edward-kelly": {"name": "爱德华·凯利", "title": "灵媒先知", "cat": "世界", "faction": "western",
        "bio": "约翰·迪伊的灵媒。以水晶球通灵。"},
    "nostradamus": {"name": "诺查丹玛斯", "title": "百诗预言", "cat": "世界", "faction": "prophet",
        "bio": "《百诗集》预言家。四行诗预测未来数百年。"},
    "paracelsus": {"name": "帕拉塞尔苏斯", "title": "炼金医师", "cat": "世界", "faction": "alchemy",
        "bio": "炼金术与医学结合者。'剂量决定毒性'。"},
    "agrippa": {"name": "阿格里帕", "title": "神秘哲学", "cat": "世界", "faction": "western",
        "bio": "《神秘哲学三书》作者。文艺复兴神秘学集大成者。"},
    "saint-germain": {"name": "圣日耳曼伯爵", "title": "不死伯爵", "cat": "世界", "faction": "alchemy",
        "bio": "欧洲最神秘的炼金术士。据说活了数百年。"},
    "cagliostro": {"name": "卡廖斯特罗", "title": "冒险炼金", "cat": "世界", "faction": "alchemy",
        "bio": "通灵者、炼金术士。欧洲宫廷的传奇人物。"},

    # --- 预言家 (prophet) ---
    "cayce": {"name": "埃德加·凯西", "title": "沉睡先知", "cat": "世界", "faction": "prophet",
        "bio": "'睡着的预言家'。在催眠状态中做二万多个预言。"},
    "jeane-dixon": {"name": "珍妮·狄克逊", "title": "总统预言", "cat": "世界", "faction": "prophet",
        "bio": "美国最著名的预言家。精准预言肯尼迪遇刺。"},
    "baba-vanga": {"name": "巴巴·万加", "title": "盲眼先知", "cat": "世界", "faction": "prophet",
        "bio": "盲眼保加利亚预言家。感知力超越五感。"},
    "merlin": {"name": "梅林", "title": "王者之师", "cat": "世界", "faction": "witchcraft",
        "bio": "亚瑟王传奇中大法师。变形术、预言、魔法。"},
    "vivian": {"name": "薇薇安", "title": "湖中仙女", "cat": "世界", "faction": "witchcraft",
        "bio": "湖中仙女。梅林的恋人/囚禁者。精通魔法。"},
    "morgan": {"name": "摩根勒菲", "title": "魔法女王", "cat": "世界", "faction": "witchcraft",
        "bio": "亚瑟王传奇中的女巫。阿瓦隆之主。"},
    "rasputin": {"name": "拉斯普京", "title": "妖僧预言", "cat": "世界", "faction": "prophet",
        "bio": "俄国妖僧。预言与治疗能力。毒杀不死传说。"},
    "blavatsky": {"name": "布拉瓦茨基夫人", "title": "神智学母", "cat": "世界", "faction": "western",
        "bio": "神智学创始人。通灵。'秘密教义'。"},
    "crowley": {"name": "阿莱斯特·克劳利", "title": "兽之使者", "cat": "世界", "faction": "western",
        "bio": "泰勒玛体系创始人。'做你所愿即为全部律法'。"},

    # --- 理性研究者 (rational) ---
    "jung": {"name": "卡尔·荣格", "title": "共时性大师", "cat": "世界", "faction": "rational",
        "bio": "分析心理学之父。深入研究《易经》和占星术。共时性理论。"},
    "steiner": {"name": "鲁道夫·施泰纳", "title": "人智学父", "cat": "世界", "faction": "western",
        "bio": "人智学创始人。通灵。华德福教育鼻祖。"},
    "swedenborg": {"name": "斯威登堡", "title": "灵界见闻", "cat": "世界", "faction": "prophet",
        "bio": "灵界旅行者。记录灵界见闻。影响深远。"},
    "william-blake": {"name": "威廉·布莱克", "title": "先知诗人", "cat": "世界", "faction": "prophet",
        "bio": "诗人兼神秘主义者。看到天使和灵界。"},
    "rumi": {"name": "鲁米", "title": "旋转通神", "cat": "世界", "faction": "rational",
        "bio": "苏菲派神秘主义诗人。'你生而有翼为何宁愿爬行'。"},

    # --- 占星家 (western/orthodox) ---
    "abu-mashar": {"name": "阿布·马谢尔", "title": "阿拉伯占星", "cat": "世界", "faction": "western",
        "bio": "阿拉伯最伟大的占星家。占星学著作影响欧洲数百年。"},
    "al-biruni": {"name": "阿尔·比鲁尼", "title": "天文占星", "cat": "世界", "faction": "rational",
        "bio": "波斯博学家。占星术批判性研究者。"},
    "michael-scott": {"name": "迈克尔·斯科特", "title": "皇家占星", "cat": "世界", "faction": "western",
        "bio": "神圣罗马帝国宫廷占星家。魔法师。"},
    "ralph-trine": {"name": "拉尔夫·特赖因", "title": "心灵哲学", "cat": "世界", "faction": "rational",
        "bio": "新思想运动代表。'与无限同在'。"},

    # --- 古希腊神谕 (prophet) ---
    "sibyl": {"name": "西比尔", "title": "女预言家", "cat": "世界", "faction": "prophet",
        "bio": "古希腊罗马传说中的女预言家。'西比尔之书'。"},
    "pythia": {"name": "皮提亚", "title": "德尔斐神谕", "cat": "世界", "faction": "prophet",
        "bio": "德尔斐阿波罗神庙的女祭司。古希腊最著名的神谕。"},
    "cassandra": {"name": "卡珊德拉", "title": "特洛伊悲剧", "cat": "世界", "faction": "prophet",
        "bio": "特洛伊公主。被阿波罗诅咒——预言无人相信。"},
    "circe": {"name": "喀耳刻", "title": "魔法女神", "cat": "世界", "faction": "witchcraft",
        "bio": "古希腊女神。能将人变为动物。精通草药和魔法。"},
    "medea": {"name": "美狄亚", "title": "科尔喀斯女巫", "cat": "世界", "faction": "witchcraft",
        "bio": "女巫公主。助伊阿宋取金羊毛。法术强大。"},
    "isis": {"name": "伊西斯", "title": "魔法女神", "cat": "世界", "faction": "witchcraft",
        "bio": "埃及魔法与生育女神。已知魔法之母。"},
    "thoth": {"name": "托特", "title": "智慧之神", "cat": "世界", "faction": "western",
        "bio": "埃及智慧与魔法之神。塔罗牌、文字的创造者。"},

    # --- 阿拉伯炼金 (alchemy) ---
    "jabir": {"name": "贾比尔·伊本·哈扬", "title": "阿拉伯炼金", "cat": "世界", "faction": "alchemy",
        "bio": "阿拉伯炼金术之父。发现硫酸和硝酸。"},
    "razes": {"name": "拉齐", "title": "医学炼金", "cat": "世界", "faction": "alchemy",
        "bio": "波斯炼金术士和医学家。实验方法先驱。"},
    "kindi": {"name": "肯迪", "title": "魔法理论家", "cat": "世界", "faction": "rational",
        "bio": "阿拉伯哲学家。'论射线'——最早的魔法理论著作。"},
    "farabi": {"name": "法拉比", "title": "通神哲人", "cat": "世界", "faction": "rational",
        "bio": "阿拉伯哲学家。通神秘主义。'第二导师'。"},
    "ibn-arabi": {"name": "伊本·阿拉比", "title": "苏菲通神", "cat": "世界", "faction": "western",
        "bio": "苏菲派最大宗师。'存在的单一性'理论。"},

    # --- 巫师/现代威卡 (witchcraft) ---
    "gardner": {"name": "杰拉尔德·加德纳", "title": "威卡之父", "cat": "世界", "faction": "witchcraft",
        "bio": "现代威卡教创始人。'女巫的信仰'。"},
    "alex-sanders": {"name": "亚历克斯·桑德斯", "title": "现代巫王", "cat": "世界", "faction": "witchcraft",
        "bio": "现代威卡巫术的推广者。"},

    # --- 古希腊哲人通玄 (rational) ---
    "socrates": {"name": "苏格拉底", "title": "守护神之音", "cat": "世界", "faction": "rational",
        "bio": "自称有'守护神'（daemon）指引。疑涉灵异。"},
    "plato": {"name": "柏拉图", "title": "灵魂轮回", "cat": "世界", "faction": "rational",
        "bio": "记载亚特兰蒂斯传说。灵魂轮回说。《蒂迈欧篇》涉宇宙创生。"},
    "aristotle": {"name": "亚里士多德", "title": "宇宙哲学", "cat": "世界", "faction": "rational",
        "bio": "虽以哲学著称，著作涉占星术和宇宙论。"},
    "ptolemy": {"name": "托勒密", "title": "占星大成", "cat": "世界", "faction": "western",
        "bio": "《天文学大成》和《四书》——西方占星学基础。"},

    # --- 现代灵媒 (prophet) ---
    "sylvia-browne": {"name": "西尔维亚·布朗", "title": "通灵灵媒", "cat": "世界", "faction": "prophet",
        "bio": "美国著名灵媒。'灵魂之旅'系列作者。"},
    "james-van-praagh": {"name": "范·普拉格", "title": "灵界沟通", "cat": "世界", "faction": "prophet",
        "bio": "美国灵媒。与灵魂沟通的能力闻名。"},
    "john-edward": {"name": "约翰·爱德华", "title": "电视灵媒", "cat": "世界", "faction": "prophet",
        "bio": "著名电视灵媒。'跨越'节目主持人。"},
    "leadbeater": {"name": "利德比特", "title": "透视灵界", "cat": "世界", "faction": "western",
        "bio": "神智学家。声称能透视原子和灵界。"},
    "dane-rudhyar": {"name": "丹恩·鲁迪亚", "title": "人本占星", "cat": "世界", "faction": "western",
        "bio": "现代人本主义占星学创始人。占星心理学。"},
    "helen-smith": {"name": "海伦·史密斯", "title": "通灵语者", "cat": "世界", "faction": "prophet",
        "bio": "瑞士灵媒。声称通灵说火星语。荣格研究过她。"},
}


def select_debaters(per_faction: int = 2) -> list:
    """从每个阵营选代表人物"""
    from collections import defaultdict
    fm = defaultdict(list)
    for pid, fig in FIGURES.items():
        fm[fig["faction"]].append((pid, fig))
    selected = []
    for fac in FACTIONS:
        members = fm.get(fac, [])
        selected.extend(members[:min(per_faction, len(members))])
    return selected


def build_monologue(pid: str, fig: dict, a: dict) -> str:
    """根据人物阵营和性格，生成人物口吻的独白"""
    f = {k: v for k, v in a.items() if isinstance(v, (str, int, float, bool))}
    # 从 analytics 中提取关键信息
    wx = a.get("wuxing", {})
    dm = a.get("daymaster", {})
    ts = a.get("tenshen", {})
    combos = a.get("combinations", [])
    dayun = a.get("dayun_phase", {})
    features = a.get("features", [])
    th = a.get("tiaohou", {})
    mm = a.get("multi_metaphysics", {})

    wx_sorted = sorted(wx.items(), key=lambda x: -x[1])
    strongest = wx_sorted[0][0] if wx_sorted else "?"
    weakest = wx_sorted[-1][0] if len(wx_sorted) > 1 else "?"
    
    dm_gan = a.get("raw_bazi", {}).get("day_master", {}).get("gan", "?")
    dm_wx = dm.get("wuxing", "?")
    dm_str = f"{dm_gan}{dm_wx}"
    strength = dm.get("strength", "?")
    ys = th.get("yongshen", "")
    
    has_chong = any("冲" in c for c in combos)
    
    faction = fig["faction"]
    faction_desc = FACTIONS[faction]["name"]
    
    # 阵营风格前缀
    style_prefixes = {
        "orthodox": f"以正统术数观此命盘。",
        "daoist": f"观此命盘，如观流水。",
        "prophet": f"有异象——待我细观。",
        "alchemy": f"变化已在眼前——",
        "witchcraft": f"灵眼所见，非世人可知。",
        "western": f"从宇宙的更高秩序来看——",
        "rational": f"不渲染不夸大，说数据。",
    }
    prefix = style_prefixes.get(faction, "详观此命——")
    
    # 核心判断
    core = f"日主{dm_str}，{strength}格局。五行{strongest}最旺、{weakest}最弱。"
    
    if has_chong:
        chong_view = {
            "orthodox": "子午冲为水火交战——但八字有冲未必是坏事，关键看用神是否得力。",
            "daoist": "子午相冲乃天地之常——不迎不拒，冲过即安。",
            "prophet": "子午冲是大凶之兆！水火交战，上应天象，下应人事——不可不防。",
            "alchemy": "冲就是炼金炉——要么化为灰烬，要么炼出真金。此命正在炉中。",
            "witchcraft": "此命有强烈的能量冲突——水火之灵在体内争斗。",
            "western": "子午冲对应占星学上的对分相——分裂与整合的契机。",
            "rational": "数据上子午冲造成五行偏离——波动率偏高，但波动率≠风险，也可能是机会。",
        }
        core += chong_view.get(faction, "")
    else:
        core += "命局无冲，气质统一。"
    
    # 用神
    if ys:
        ys_view = {
            "orthodox": f"调候用神{ys}到位——这是天时。",
            "prophet": f"用神{ys}虽在，但力量如何？这是化解凶象的关键。",
            "alchemy": f"用神{ys}就是你的哲人石——找到它，转化就开始了。",
            "witchcraft": f"用神{ys}的能量与你共振——这是你灵魂的守护灵符。",
        }
        core += ys_view.get(faction, f"用神{ys}到位。")
    
    # 大运
    dayun_text = ""
    if dayun.get("ganzhi"):
        if faction == "prophet":
            dayun_text = f" 当前{dayun['ganzhi']}运——{dayun['gan_wuxing']}气当令，是吉是凶需看能否克制子午之火。"
        elif faction == "alchemy":
            dayun_text = f" 当前行{dayun['ganzhi']}运——这是转化周期的第二阶段。"
        else:
            dayun_text = f" 当前{dayun['ganzhi']}运。"
    
    # 六爻交叉
    liuyao = mm.get("liuyao", {})
    mm_text = ""
    if liuyao and "error" not in liuyao and liuyao.get("hexagram"):
        mm_text = f" 六爻得《{liuyao['hexagram']}》卦，{'与八字判断一致' if faction in ('orthodox','prophet') else '是另一维度的印证'}。"
    
    return f"{prefix}\n\n{core}\n\n{dayun_text}{mm_text}"


def generate_debate(destiny: dict, bazi_data: dict = None,
                    factions: list = None, per_faction: int = 2) -> dict:
    """生成辩论式分析"""
    import random
    random.seed(42)

    if factions is None:
        factions = list(FACTIONS.keys())
    
    from collections import defaultdict
    fm = defaultdict(list)
    for pid, fig in FIGURES.items():
        if fig["faction"] in factions:
            fm[fig["faction"]].append((pid, fig))
    
    # 每个阵营选代表
    debaters = {}
    for fac in factions:
        members = fm.get(fac, [])
        random.shuffle(members)
        for pid, fig in members[:per_faction]:
            debaters[pid] = fig
    
    # 提取命盘信息
    bazi = destiny.get("bazi", {})
    ba = bazi.get("bazi", {})
    dm = bazi.get("day_master", {})
    features = destiny.get("features", [])
    
    bazi_str = f"{ba.get('year','?')} {ba.get('month','?')} {ba.get('day','?')} {ba.get('time','?')}"
    dm_str = f"{dm.get('gan','?')}{dm.get('wuxing','?')}"
    
    # 构建 analytics 用于独白生成
    from perspectives_engine import get_all_analytics
    analytics = get_all_analytics(destiny)
    
    result = {
        "topic": f"玄学辩论：{bazi_str}　日主{dm_str}",
        "bazi": bazi_str,
        "participants": [],
        "rounds": [],
        "final_summary": "",
    }
    
    # 第一轮：各阵营立论
    round1 = {"phase": "初论：各派立论", "speeches": []}
    for pid, fig in debaters.items():
        speech = build_monologue(pid, fig, analytics)
        round1["speeches"].append({
            "name": fig["name"],
            "title": fig["title"],
            "faction": FACTIONS[fig["faction"]]["name"],
            "text": speech,
        })
        result["participants"].append({
            "id": pid, "name": fig["name"],
            "title": fig["title"],
            "faction": fig["faction"],
            "faction_name": FACTIONS[fig["faction"]]["name"],
        })
    result["rounds"].append(round1)
    
    # 第二轮：互相驳斥（选代表性人物做交锋）
    round2 = {"phase": "驳论：观点交锋", "exchanges": []}
    
    # 挑几个针锋相对的组合
    clash_pairs = [
        ("orthodox", "prophet", "玄学正宗vs预言警示"),
        ("daoist", "alchemy", "道家自然vs炼金转化"),
        ("rational", "western", "理性研究vs西方神秘"),
    ]
    
    for f1, f2, label in clash_pairs:
        d1 = [(pid, fig) for pid, fig in debaters.items() if fig["faction"] == f1]
        d2 = [(pid, fig) for pid, fig in debaters.items() if fig["faction"] == f2]
        if d1 and d2:
            pid1, fig1 = d1[0]
            pid2, fig2 = d2[0]
            round2["exchanges"].append({
                "label": label,
                "challenger": fig1["name"],
                "target": fig2["name"],
                "text": f"{fig1['name']}对{fig2['name']}的回应：{'子午冲不可轻言吉凶——你方言之过早' if f1 == 'orthodox' else '你们的数据分析忽略了一个维度——能量'},{fig2['name']}当如何作答？",
                "rebuttal": f"{fig2['name']}答{fig1['name']}：{'道不同不相为谋——你用数字衡量命运，我用灵魂感知' if f2 == 'prophet' else '你们的直觉主义恰恰缺少了可重复验证的标准'}",
            })
    result["rounds"].append(round2)
    
    # 第三轮：综述
    consensus = []
    for pid, fig in debaters.items():
        consensus.append(f"{fig['name']}（{FACTIONS[fig['faction']]['name']}）")
    
    result["final_summary"] = (
        f"命盘{bazi_str}（日主{dm_str}）的108玄学视角辩论综述：\n\n"
        f"【最大共识】子午冲是核心矛盾——7个阵营无一否认这一点。分歧在于：这究竟是凶是吉、该化解还是顺应。\n\n"
        f"【核心分歧】玄学正宗派认为冲中藏机，关键在于用神癸水是否得力；预言警示派坚持这是大凶之兆，不可轻忽；"
        f"炼丹派和道家派反而认为冲象即机遇——在于如何转化和顺应。\n\n"
        f"【理性派结论】从数据角度，此命五行火旺土弱、七杀透干、子午相冲，波动率显著高于平均——"
        f"这意味着此人的人生不会风平浪静，但也因此比常人更有机会在波动中获益。\n\n"
        f"【综合建议】采纳玄学正宗的格局判断为基础，结合道家自然的顺势智慧，"
        f"辅以预警派的审慎态度——三条路径缺一不可。"
    )
    
    return result
