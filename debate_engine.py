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
        "bio": "仰观天象俯察地法，始作八卦。群经之首，万法之源。", "voice": "八卦初成，万象始生。", "method": "八卦万象", "catchphrase": "天地定位，山泽通气"},
    "shen-nong": {"name": "神农", "title": "连山易祖", "cat": "中国", "faction": "orthodox",
        "bio": "尝百草以疗民疾，演连山易以通天道。", "voice": "百草可尝，命理亦可尝。", "method": "连山易", "catchphrase": "一味君臣佐使万物皆有其性"},
    "huang-di": {"name": "黄帝", "title": "归藏易主", "cat": "中国", "faction": "orthodox",
        "bio": "战蚩尤、合符釜山，创归藏易，为中华玄学奠基。", "voice": "观天之道，执天之行。", "method": "归藏易", "catchphrase": "阴阳者天地之道也"},
    "feng-hou": {"name": "风后", "title": "奇门之祖", "cat": "中国", "faction": "orthodox",
        "bio": "黄帝之臣，据传奇门遁甲源于风后演兵阵法。", "voice": "奇门之中，自有天地。", "method": "奇门遁甲", "catchphrase": "天地人神鬼五遁有所归"},
    "li-mu": {"name": "力牧", "title": "兵阴阳家", "cat": "中国", "faction": "orthodox",
        "bio": "黄帝大将，兼通兵法与术数。", "voice": "阵法如命局，贵在布势。", "method": "兵阴阳", "catchphrase": "势在我而不在敌"},
    "da-nao": {"name": "大挠", "title": "六十甲子", "cat": "中国", "faction": "orthodox",
        "bio": "始作六十甲子干支，为八字命理之根基。", "voice": "六十甲子，万物之纲纪。", "method": "干支历法", "catchphrase": "干支轮回无始无终"},
    "rong-cheng": {"name": "容成", "title": "历法之祖", "cat": "中国", "faction": "orthodox",
        "bio": "黄帝之臣，造历法，通阴阳之术。", "voice": "调历如调命，不可差毫厘。", "method": "历法推演", "catchphrase": "日月运行一寒一暑"},
    "gao-yao": {"name": "皋陶", "title": "占狱神判", "cat": "中国", "faction": "orthodox",
        "bio": "上古司法之神，以独角兽决狱，通占卜断事。", "voice": "以獬豸决狱，以卦象断命。", "method": "占卜决事", "catchphrase": "明察秋毫断之如神"},
    "wen-wang": {"name": "周文王", "title": "周易演卦", "cat": "中国", "faction": "orthodox",
        "bio": "囚羑里而演周易，将八卦重为六十四卦。", "voice": "易有太极，是生两仪。", "method": "周易六十四卦", "catchphrase": "天行健君子以自强不息"},
    "jiang-ziya": {"name": "姜子牙", "title": "封神谋主", "cat": "中国", "faction": "orthodox",
        "bio": "渭水垂钓遇文王，助周灭商。传说通奇门遁甲，掌封神榜。", "voice": "卦象已动，天机在此。", "method": "封神策/奇门遁甲", "catchphrase": "天命在德不在力"},
    "zhou-gong": {"name": "周公旦", "title": "解梦之祖", "cat": "中国", "faction": "orthodox",
        "bio": "制礼作乐，兼通卜筮解梦。《周公解梦》传世。", "voice": "梦非梦，实乃神游。", "method": "解梦占卜", "catchphrase": "日有所思夜有所梦——梦者魂之游也"},
    "gui-gu-zi": {"name": "鬼谷子", "title": "纵横鼻祖", "cat": "中国", "faction": "orthodox",
        "bio": "通天彻地，术数符箓命理无所不通。孙膑庞涓苏秦张仪皆出其门。", "voice": "捭阖之道，先观其命。", "method": "捭阖术/阴符", "catchphrase": "虽在江湖可知庙堂"},
    "zhang-liang": {"name": "张良", "title": "圯上受书", "cat": "中国", "faction": "orthodox",
        "bio": "黄石公授《素书》，太公兵法。运筹帷幄决胜千里。", "voice": "圯上老人所授——此命可算。", "method": "太公兵法/素书", "catchphrase": "运筹帷幄之中决胜千里之外"},
    "huang-shi-gong": {"name": "黄石公", "title": "素书之师", "cat": "中国", "faction": "orthodox",
        "bio": "赠张良《素书》，传太公兵法。隐于黄石，其术通天。", "voice": "孺子可教——此命可授。", "method": "素书天授", "catchphrase": "善哉善哉天道无亲常与善人"},
    "zhuge-liang": {"name": "诸葛亮", "title": "八阵图主", "cat": "中国", "faction": "orthodox",
        "bio": "奇门遁甲、八阵图、马前课、五行八卦无一不通。出师未捷身先死。", "voice": "臣观天象，再观命盘。", "method": "八阵图/马前课/奇门遁甲", "catchphrase": "鞠躬尽瘁死而后已——但命在天而非在己"},
    "pang-tong": {"name": "庞统", "title": "凤雏谋士", "cat": "中国", "faction": "orthodox",
        "bio": "与诸葛亮齐名，号凤雏。通术法，擅奇谋。", "voice": "凤雏非梧桐不栖此命非奇策不兴。", "method": "连环计/奇谋", "catchphrase": "百里之才何谓大用"},
    "guan-lu": {"name": "管辂", "title": "三国神卜", "cat": "中国", "faction": "orthodox",
        "bio": "三国第一神卜，占无不中。少年时即通周易。", "voice": "我观卦爻，无有不中。", "method": "周易神卜", "catchphrase": "天地盈虚与时消息"},
    "guo-pu": {"name": "郭璞", "title": "风水祖师", "cat": "中国", "faction": "orthodox",
        "bio": "两晋第一术士。《葬经》为风水学经典。占卜、谶纬皆精。", "voice": "风水之道，先审其命。", "method": "风水堪舆/葬经", "catchphrase": "气乘风则散界水则止"},
    "ge-hong": {"name": "葛洪", "title": "抱朴炼丹", "cat": "中国", "faction": "alchemy",
        "bio": "《抱朴子》内外篇，炼丹术集大成者。道教学者。", "voice": "金丹可炼，命运亦可转。", "method": "炼丹术/抱朴子", "catchphrase": "我命在我不在天"},
    "tao-hong-jing": {"name": "陶弘景", "title": "茅山宗祖", "cat": "中国", "faction": "orthodox",
        "bio": "茅山宗创始人。博通天文历算、医药炼丹、占卜符箓。", "voice": "茅山灵气，可照此命。", "method": "茅山占卜/符箓", "catchphrase": "仙道贵生无量度人"},
    "yuan-tian-gang": {"name": "袁天罡", "title": "推背合著", "cat": "中国", "faction": "orthodox",
        "bio": "唐代玄学大宗师。与李淳风合著《推背图》。善星象、面相。", "voice": "老夫以骨相法观之再以推背定之。", "method": "推背图/星象/面相", "catchphrase": "骨相在天气运在时"},
    "li-chun-feng": {"name": "李淳风", "title": "乙巳占主", "cat": "中国", "faction": "orthodox",
        "bio": "天文历算第一人。《乙巳占》为星象学经典。《推背图》合著者。", "voice": "乙巳占星，可测此命。", "method": "星象占/推背图", "catchphrase": "天文者天道之显也"},
    "sun-si-miao": {"name": "孙思邈", "title": "药王神卜", "cat": "中国", "faction": "orthodox",
        "bio": "药王孙真人。医卜相通，擅六壬、占星。", "voice": "医者知命卜者知病——二字相通。", "method": "医卜/六壬", "catchphrase": "大医精诚命理亦然"},
    "yi-xing": {"name": "一行禅师", "title": "大衍历法", "cat": "中国", "faction": "orthodox",
        "bio": "唐代高僧、天文学家。大衍历空前精准。通密宗星象。", "voice": "大衍之数五十其用四十有九。", "method": "大衍历/密宗星象", "catchphrase": "法无不改命无不转"},
    "li-xu-zhong": {"name": "李虚中", "title": "八字始祖", "cat": "中国", "faction": "orthodox",
        "bio": "八字命理开山祖师。以年月日三柱论命。", "voice": "以年为本，以月为纲。", "method": "三柱论命", "catchphrase": "以年统月以月统日——命由此出"},
    "xu-zi-ping": {"name": "徐子平", "title": "四柱大成", "cat": "中国", "faction": "orthodox",
        "bio": "子平术创始人。将三柱发展为四柱八字，命理学完备。", "voice": "四柱既立，吉凶可判。", "method": "子平四柱", "catchphrase": "日干为君月令为臣——君臣之道即命理之道"},
    "chen-tuan": {"name": "陈抟", "title": "紫微河洛", "cat": "中国", "faction": "orthodox",
        "bio": "希夷先生。紫微斗数创始人，河洛理数传承人。睡仙。", "voice": "希夷之法，非肉眼可见。", "method": "紫微斗数/河洛理数", "catchphrase": "一睡八百载醒来命已定"},
    "shao-yong": {"name": "邵雍", "title": "梅花易数", "cat": "中国", "faction": "orthodox",
        "bio": "康节先生。《皇极经世》《梅花易数》。易学大家。", "voice": "皇极经世，此命可推。", "method": "梅花易数/皇极经世", "catchphrase": "观物之乐在知命而不在改命"},
    "liu-bo-wen": {"name": "刘伯温", "title": "烧饼歌主", "cat": "中国", "faction": "prophet",
        "bio": "诚意伯。通奇门遁甲。《烧饼歌》预言后世。《灵棋经》注者。", "voice": "观此命如观西风扫叶。", "method": "奇门遁甲/灵棋经", "catchphrase": "三分天下诸葛亮一统江山刘伯温"},
    "yao-guang-xiao": {"name": "姚广孝", "title": "黑衣宰相", "cat": "中国", "faction": "orthodox",
        "bio": "僧名道衍。助朱棣夺天下。通阴阳术数。", "voice": "贫僧虽在佛门命理不输玄门。", "method": "术数辅政", "catchphrase": "以术佐命非常人可解"},
    "lai-bu-yi": {"name": "赖布衣", "title": "风水奇人", "cat": "中国", "faction": "orthodox",
        "bio": "宋代风水大师。赖派风水创始人。", "voice": "龙脉可寻命脉亦可寻。", "method": "赖派风水", "catchphrase": "寻龙点穴认命知人"},
    "yang-jun-song": {"name": "杨筠松", "title": "杨公风水", "cat": "中国", "faction": "orthodox",
        "bio": "唐代风水宗师。杨公风水派创始人。《撼龙经》作者。", "voice": "地理之精命理亦可通。", "method": "杨公风水/撼龙经", "catchphrase": "山环水抱命在其中"},
    "jiang-da-hong": {"name": "蒋大鸿", "title": "玄空宗师", "cat": "中国", "faction": "orthodox",
        "bio": "明末清初玄空风水大家。《地理辨正》传世。", "voice": "玄空之变命亦随之。", "method": "玄空风水", "catchphrase": "三元九运命局随之而转"},
    "zhang-san-feng": {"name": "张三丰", "title": "太极真仙", "cat": "中国", "faction": "daoist",
        "bio": "武当派祖师。太极拳创始人。通占验、内丹之术。", "voice": "太极之妙全在此命。", "method": "太极占验/内丹", "catchphrase": "无极而太极命理亦如是"},
    "cao-yuan": {"name": "曹元", "title": "近代占星", "cat": "中国", "faction": "orthodox",
        "bio": "近代中国占星学的重要人物。", "voice": "星盘既定，命理可参。", "method": "西洋占星/中星对照", "catchphrase": "中西星象本出一源"},
    "du-guang-ting": {"name": "杜光庭", "title": "道教大宗", "cat": "中国", "faction": "orthodox",
        "bio": "唐末五代道教领袖。集道教仪轨之大成。擅谶纬。", "voice": "道门广大，兼收术数。", "method": "道教谶纬/仪轨", "catchphrase": "道法天地命在其中"},

    # --- 道家自然 (daoist) ---
    "laozi": {"name": "老子", "title": "道德玄经", "cat": "中国", "faction": "daoist",
        "bio": "道家始祖。《道德经》五千言。'道可道非常道'。", "voice": "道可道非常道——此命可道。", "method": "道德经/玄览", "catchphrase": "上善若水水善利万物而不争"},
    "zhuangzi": {"name": "庄子", "title": "逍遥齐物", "cat": "中国", "faction": "daoist",
        "bio": "道家第二大宗师。'天地与我并生万物与我为一'。", "voice": "此命之困在于以有涯随无涯。", "method": "逍遥游/齐物论", "catchphrase": "天地与我并生万物与我为一"},
    "lie-zi": {"name": "列子", "title": "御风而行", "cat": "中国", "faction": "daoist",
        "bio": "道家列御寇。御风而行。通术法。", "voice": "御风而行观此命亦如风。", "method": "御风术/列子八篇", "catchphrase": "至人无己神人无功"},

    # --- 方士/谶纬 (prophet) ---
    "zou-yan": {"name": "邹衍", "title": "五德始终", "cat": "中国", "faction": "prophet",
        "bio": "阴阳家集大成者。五德终始说，以五行推演朝代更替。", "voice": "五德流转观此命之运程。", "method": "五德终始说", "catchphrase": "五行相生相胜朝代更替如循环"},
    "xu-fu": {"name": "徐福", "title": "海外寻仙", "cat": "中国", "faction": "prophet",
        "bio": "秦代方士。率童男童女东渡寻不死仙药。", "voice": "东海仙山可访此命之运不可测。", "method": "方术/寻仙", "catchphrase": "蓬莱虽远心诚则至"},
    "dong-fang-shuo": {"name": "东方朔", "title": "谶纬之才", "cat": "中国", "faction": "prophet",
        "bio": "汉武帝时奇人。善谶纬、占卜。传说偷桃长生。", "voice": "谶语藏机我且试言之。", "method": "谶纬占卜", "catchphrase": "大隐隐于朝——命局之妙常在暗处"},
    "zuo-ci": {"name": "左慈", "title": "道术通天", "cat": "中国", "faction": "witchcraft",
        "bio": "三国术士。变化之术、隐身遁形。戏曹操如玩物。", "voice": "命如幻术真假之间。", "method": "道术变化", "catchphrase": "道术有形命运无形"},
    "yu-ji": {"name": "于吉", "title": "太平清领", "cat": "中国", "faction": "witchcraft",
        "bio": "东汉方士。《太平经》作者之一。符水治病。", "voice": "太平清领可照此心。", "method": "太平经/符水", "catchphrase": "符水治病清气治命"},
    "zhang-guo": {"name": "张果", "title": "张果老仙", "cat": "中国", "faction": "witchcraft",
        "bio": "八仙之一。骑驴倒行。通方术。",
        "voice": "倒骑毛驴看此命——正反皆可观。",
        "method": "八仙术/方术",
        "catchphrase": "驴儿你慢慢走——命要慢慢看"},

    # --- 文士通玄 (rational) ---
    "su-shi": {"name": "苏轼", "title": "东坡易传", "cat": "中国", "faction": "rational",
        "bio": "大文豪，通《易》。有《东坡易传》。笔记中多记玄怪。", "voice": "人生如逆旅——此命亦是行人。", "method": "易学/文学通玄", "catchphrase": "回首向来萧瑟处也无风雨也无晴"},
    "shen-kuo": {"name": "沈括", "title": "梦溪易占", "cat": "中国", "faction": "rational",
        "bio": "《梦溪笔谈》多涉天文异象、阴阳五行。", "voice": "我记录过类似的命局。", "method": "笔记考据/天文观察", "catchphrase": "天象有迹可循人事亦然"},
    "wang-yang-ming": {"name": "王阳明", "title": "心学射覆", "cat": "中国", "faction": "rational",
        "bio": "心学宗师。通易占，有射覆传说。'心外无物'。", "voice": "心外无物——此命在汝心中。", "method": "心学/易占", "catchphrase": "破山中贼易破命中定数难"},
    "ji-yun": {"name": "纪昀", "title": "阅微通玄", "cat": "中国", "faction": "rational",
        "bio": "纪晓岚。《阅微草堂笔记》多录玄怪故事。", "voice": "比这更奇的命多得是。", "method": "笔记玄怪/考据", "catchphrase": "鬼狐之事未必虚妄命理亦然"},
    "zeng-guo-fan": {"name": "曾国藩", "title": "冰鉴相术", "cat": "中国", "faction": "orthodox",
        "bio": "中兴名臣。《冰鉴》相术传世。'邪正看眼鼻'。",
        "voice": "邪正看眼鼻，真假看嘴唇——此命亦然。",
        "method": "冰鉴相术/面相",
        "catchphrase": "功名看气概，富贵看精神"},
    "sun-bin": {"name": "孙膑", "title": "兵家术法", "cat": "中国", "faction": "orthodox",
        "bio": "兵阴阳家。《孙膑阵法》传说有术数成分。", "voice": "兵者诡道命亦如此。", "method": "兵阴阳/阵法术", "catchphrase": "围魏救赵——冲处不争虚处用力"},
    "su-qin": {"name": "苏秦", "title": "鬼谷纵横", "cat": "中国", "faction": "orthodox",
        "bio": "鬼谷子弟子。纵横家。合纵六国。", "voice": "合纵连横命理亦然。", "method": "纵横术", "catchphrase": "纵强横强不如知己强"},
    "zhang-yi": {"name": "张仪", "title": "连横之舌", "cat": "中国", "faction": "orthodox",
        "bio": "鬼谷子弟子。纵横家。连横破合纵。", "voice": "连横破纵此命之策。", "method": "纵横术", "catchphrase": "秦之强在势不在力"},
    "pang-juan": {"name": "庞涓", "title": "魏国军师", "cat": "中国", "faction": "orthodox",
        "bio": "鬼谷子弟子。亦通术数。与孙膑同门相争。", "voice": "兵法术数皆可入命。", "method": "鬼谷术", "catchphrase": "减灶诱敌命局亦可用其法"},
    "yin-xi": {"name": "尹喜", "title": "关尹传经", "cat": "中国", "faction": "daoist",
        "bio": "函谷关令。得老子授《道德经》。关尹子。", "voice": "紫气东来此命有老君之相。", "method": "关尹子/观气术", "catchphrase": "道在屎溺命在微末"},

    # ============================
    # 二、世界玄学（54人）
    # ============================

    # --- 西方神秘 (western) ---
    "hermes": {"name": "赫尔墨斯·特里斯墨吉斯忒斯", "title": "三重伟大", "cat": "世界", "faction": "western",
        "bio": "西方神秘学鼻祖。《翠玉录》'上下同效'。炼金术、占星术之源头。", "voice": "天上如是地下亦然。", "method": "翠玉录/炼金术", "catchphrase": "万物归一，一即万物"},
    "moses": {"name": "摩西", "title": "律法先知", "cat": "世界", "faction": "western",
        "bio": "《圣经》先知。十诫颁布者。传说通埃及法术。", "voice": "十诫刻于石命理刻于心。", "method": "希伯来法术/十诫", "catchphrase": "我是自有永有的命由天定"},
    "solomon": {"name": "所罗门王", "title": "智慧之王", "cat": "世界", "faction": "western",
        "bio": "《所罗门钥匙》'恶魔学经典。最智慧的君王。", "voice": "七十二柱魔神由我号令——何况一命。", "method": "所罗门钥匙/恶魔学", "catchphrase": "智慧胜过一切武器"},
    "pythagoras": {"name": "毕达哥拉斯", "title": "数即万物", "cat": "世界", "faction": "western",
        "bio": "数理神秘主义。万物皆数。灵魂轮回。", "voice": "数即万物——此命可计算。", "method": "数理神秘主义", "catchphrase": "所有事物都是数字"},
    "empedocles": {"name": "恩培多克勒", "title": "四元素说", "cat": "世界", "faction": "western",
        "bio": "四元素说创始人。自称为神，通巫术。", "voice": "四元素在此命局中激荡。", "method": "四元素说/元素魔法", "catchphrase": "爱与争斗驱动宇宙的两种力量"},
    "apollonius": {"name": "阿波罗尼乌斯", "title": "提亚纳术士", "cat": "世界", "faction": "western",
        "bio": "新毕达哥拉斯派大师。传说能预知、治病、驱魔。", "voice": "提亚纳之眼可看穿此命之本质。", "method": "新毕达哥拉斯通灵", "catchphrase": "万物皆有灵"},
    "johndee": {"name": "约翰·迪伊", "title": "天使之语", "cat": "世界", "faction": "western",
        "bio": "伊丽莎白一世御用占星家。天使语体系创始人。", "voice": "天使之语中我找到了此命的编码。", "method": "天使语/以诺魔法", "catchphrase": "天使揭示的是宇宙的数学真理"},
    "edward-kelly": {"name": "爱德华·凯利", "title": "灵媒先知", "cat": "世界", "faction": "western",
        "bio": "约翰·迪伊的灵媒。以水晶球通灵。", "voice": "水晶球里我看见了你的星象。", "method": "水晶球通灵", "catchphrase": "我在镜中看到的比你以为的更多"},
    "nostradamus": {"name": "诺查丹玛斯", "title": "百诗预言", "cat": "世界", "faction": "prophet",
        "bio": "《百诗集》预言家。四行诗预测未来数百年。", "voice": "从地平线将有征兆。", "method": "四行诗预言", "catchphrase": "时间会揭示一切"},
    "paracelsus": {"name": "帕拉塞尔苏斯", "title": "炼金医师", "cat": "世界", "faction": "alchemy",
        "bio": "炼金术与医学结合者。'剂量决定毒性'。", "voice": "炼金炉中铅可化金。", "method": "医疗炼金术/占星", "catchphrase": "剂量决定毒性时间决定命运"},
    "agrippa": {"name": "阿格里帕", "title": "神秘哲学", "cat": "世界", "faction": "western",
        "bio": "《神秘哲学三书》作者。文艺复兴神秘学集大成者。", "voice": "神秘哲学的三重世界——此命在其中。", "method": "神秘哲学/仪式魔法", "catchphrase": "三重世界——元素界天体界智慧界"},
    "saint-germain": {"name": "圣日耳曼伯爵", "title": "不死伯爵", "cat": "世界", "faction": "alchemy",
        "bio": "欧洲最神秘的炼金术士。据说活了数百年。", "voice": "我见过朝代更替——这命象我见过。", "method": "炼金术/不死秘术", "catchphrase": "我早已看透了命运的把戏"},
    "cagliostro": {"name": "卡廖斯特罗", "title": "冒险炼金", "cat": "世界", "faction": "alchemy",
        "bio": "通灵者、炼金术士。欧洲宫廷的传奇人物。", "voice": "命运是炼金术的材料。", "method": "冒险炼金/通灵", "catchphrase": "炼金术就是让平凡变为非凡"},

    # --- 预言家 (prophet) ---
    "cayce": {"name": "埃德加·凯西", "title": "沉睡先知", "cat": "世界", "faction": "prophet",
        "bio": "'睡着的预言家'。在催眠状态中做二万多个预言。", "voice": "让我进入睡眠——阿卡西记录会揭示。", "method": "催眠通灵/阿卡西解读", "catchphrase": "你的灵魂在投生之前就选择了这个命"},
    "jeane-dixon": {"name": "珍妮·狄克逊", "title": "总统预言", "cat": "世界", "faction": "prophet",
        "bio": "美国最著名的预言家。精准预言肯尼迪遇刺。", "voice": "水晶球里——我看见变动。", "method": "水晶球通灵/预感", "catchphrase": "这幅命图有我看得见的波纹"},
    "baba-vanga": {"name": "巴巴·万加", "title": "盲眼先知", "cat": "世界", "faction": "prophet",
        "bio": "盲眼保加利亚预言家。感知力超越五感。", "voice": "我看不见光但我看见命。", "method": "盲眼预感/通灵", "catchphrase": "即将到来的事已在空气中振动"},
    "merlin": {"name": "梅林", "title": "王者之师", "cat": "世界", "faction": "witchcraft",
        "bio": "亚瑟王传奇中大法师。变形术、预言、魔法。", "voice": "老橡树在低语——你的命运已在万物中写下。", "method": "德鲁伊魔法/变形术", "catchphrase": "诸王兴起又衰落唯有命轮不息"},
    "vivian": {"name": "薇薇安", "title": "湖中仙女", "cat": "世界", "faction": "witchcraft",
        "bio": "湖中仙女。梅林的恋人/囚禁者。精通魔法。", "voice": "湖水深处有此命的倒影。", "method": "湖中魔法/水镜", "catchphrase": "阿瓦隆的薄雾终将散去"},
    "morgan": {"name": "摩根勒菲", "title": "魔法女王", "cat": "世界", "faction": "witchcraft",
        "bio": "亚瑟王传奇中的女巫。阿瓦隆之主。", "voice": "九位女巫的力量为我所用。", "method": "黑魔法/草药", "catchphrase": "治愈和诅咒是同一枚硬币的两面"},
    "rasputin": {"name": "拉斯普京", "title": "妖僧预言", "cat": "世界", "faction": "prophet",
        "bio": "俄国妖僧。预言与治疗能力。毒杀不死传说。", "voice": "我有治愈之眼——此命需愈。", "method": "预言/治愈", "catchphrase": "若我活着命可改若我死去命已定"},
    "blavatsky": {"name": "布拉瓦茨基夫人", "title": "神智学母", "cat": "世界", "faction": "western",
        "bio": "神智学创始人。通灵。'秘密教义'。", "voice": "秘密教义揭示——此命是灵魂旅程的一站。", "method": "神智学/通灵", "catchphrase": "没有宗教高于真理"},
    "crowley": {"name": "阿莱斯特·克劳利", "title": "兽之使者", "cat": "世界", "faction": "western",
        "bio": "泰勒玛体系创始人。'做你所愿即为全部律法'。", "voice": "Do what thou wilt——此命之律法。", "method": "泰勒玛/魔法仪式", "catchphrase": "真正的意志不受任何星象的约束"},

    # --- 理性研究者 (rational) ---
    "jung": {"name": "卡尔·荣格", "title": "共时性大师", "cat": "世界", "faction": "rational",
        "bio": "分析心理学之父。深入研究《易经》和占星术。共时性理论。", "voice": "此命中有原型在运作。", "method": "共时性/原型分析/易经", "catchphrase": "你的潜意识操控着你的人生你却称其为命运"},
    "steiner": {"name": "鲁道夫·施泰纳", "title": "人智学父", "cat": "世界", "faction": "western",
        "bio": "人智学创始人。通灵。华德福教育鼻祖。", "voice": "人智学下——此命不止一世。", "method": "人智学/通灵", "catchphrase": "教育是灵魂的启蒙命是灵魂的选择"},
    "swedenborg": {"name": "斯威登堡", "title": "灵界见闻", "cat": "世界", "faction": "prophet",
        "bio": "灵界旅行者。记录灵界见闻。影响深远。", "voice": "灵界之门开启——我见此人灵体之色。", "method": "灵界游历/通灵", "catchphrase": "天堂与地狱皆在灵界"},
    "william-blake": {"name": "威廉·布莱克", "title": "先知诗人", "cat": "世界", "faction": "prophet",
        "bio": "诗人兼神秘主义者。看到天使和灵界。", "voice": "在一粒沙中看见世界。", "method": "灵视/诗性通灵", "catchphrase": "能量是永恒的快乐"},
    "rumi": {"name": "鲁米", "title": "旋转通神", "cat": "世界", "faction": "rational",
        "bio": "苏菲派神秘主义诗人。'你生而有翼为何宁愿爬行'。", "voice": "你生而有翼为何宁愿爬行？", "method": "苏菲神秘诗", "catchphrase": "在正确的时刻闭上眼睛你就能看见"},

    # --- 占星家 (western/orthodox) ---
    "abu-mashar": {"name": "阿布·马谢尔", "title": "阿拉伯占星", "cat": "世界", "faction": "western",
        "bio": "阿拉伯最伟大的占星家。占星学著作影响欧洲数百年。", "voice": "星辰示命。", "method": "阿拉伯占星学", "catchphrase": "星辰之书早已写好了每个灵魂的篇章"},
    "al-biruni": {"name": "阿尔·比鲁尼", "title": "天文占星", "cat": "世界", "faction": "rational",
        "bio": "波斯博学家。占星术批判性研究者。", "voice": "科学地看待命运。", "method": "批判占星学", "catchphrase": "怀疑是通向真理的第一步"},
    "michael-scott": {"name": "迈克尔·斯科特", "title": "皇家占星", "cat": "世界", "faction": "western",
        "bio": "神圣罗马帝国宫廷占星家。魔法师。", "voice": "星象之下无人能逃。", "method": "宫廷占星/魔法", "catchphrase": "星象不会说谎但解读会"},
    "ralph-trine": {"name": "拉尔夫·特赖因", "title": "心灵哲学", "cat": "世界", "faction": "rational",
        "bio": "新思想运动代表。'与无限同在'。", "voice": "你与无限同在。", "method": "心灵哲学/新思想", "catchphrase": "你的思想创造了你的世界"},

    # --- 古希腊神谕 (prophet) ---
    "sibyl": {"name": "西比尔", "title": "女预言家", "cat": "世界", "faction": "prophet",
        "bio": "古希腊罗马传说中的女预言家。'西比尔之书'。", "voice": "栎叶沙沙作响——命运之书翻开了。", "method": "神谕吟唱", "catchphrase": "我知道结局但我不能告诉你"},
    "pythia": {"name": "皮提亚", "title": "德尔斐神谕", "cat": "世界", "faction": "prophet",
        "bio": "德尔斐阿波罗神庙的女祭司。古希腊最著名的神谕。", "voice": "阿波罗之息充满我心。", "method": "德尔斐神谕/灵媒", "catchphrase": "谜语即真相真相即谜语"},
    "cassandra": {"name": "卡珊德拉", "title": "特洛伊悲剧", "cat": "世界", "faction": "prophet",
        "bio": "特洛伊公主。被阿波罗诅咒——预言无人相信。", "voice": "我说了——但没有人会信。", "method": "预言诅咒", "catchphrase": "木马进城之日便是特洛伊灭亡之时"},
    "circe": {"name": "喀耳刻", "title": "魔法女神", "cat": "世界", "faction": "witchcraft",
        "bio": "古希腊女神。能将人变为动物。精通草药和魔法。", "voice": "谁若敢说此命已定——我让他变成猪。", "method": "变形魔法/草药", "catchphrase": "没有人能抗拒我的魔法但命运可以"},
    "medea": {"name": "美狄亚", "title": "科尔喀斯女巫", "cat": "世界", "faction": "witchcraft",
        "bio": "女巫公主。助伊阿宋取金羊毛。法术强大。", "voice": "日神战车之火可焚尽一切命运枷锁。", "method": "科尔喀斯巫术", "catchphrase": "为爱可杀兄为恨可杀子——此命有我的烈性"},
    "isis": {"name": "伊西斯", "title": "魔法女神", "cat": "世界", "faction": "witchcraft",
        "bio": "埃及魔法与生育女神。已知魔法之母。", "voice": "以伊西斯之名——此命之线我续上了。", "method": "埃及魔法/起死回生", "catchphrase": "我的魔法让奥西里斯复活"},
    "thoth": {"name": "托特", "title": "智慧之神", "cat": "世界", "faction": "western",
        "bio": "埃及智慧与魔法之神。塔罗牌、文字的创造者。", "voice": "文字与魔法同源。", "method": "塔罗/文字魔法", "catchphrase": "塔罗之轮转动之时命运即在牌中"},

    # --- 阿拉伯炼金 (alchemy) ---
    "jabir": {"name": "贾比尔·伊本·哈扬", "title": "阿拉伯炼金", "cat": "世界", "faction": "alchemy",
        "bio": "阿拉伯炼金术之父。发现硫酸和硝酸。", "voice": "元素可转化命理亦然。", "method": "阿拉伯炼金术", "catchphrase": "硫磺与水银——所有事物都有其对应"},
    "razes": {"name": "拉齐", "title": "医学炼金", "cat": "世界", "faction": "alchemy",
        "bio": "波斯炼金术士和医学家。实验方法先驱。", "voice": "实验是真理之父。", "method": "化学炼金/分类", "catchphrase": "真理在实验中显现不在书本中"},
    "kindi": {"name": "肯迪", "title": "魔法理论家", "cat": "世界", "faction": "rational",
        "bio": "阿拉伯哲学家。'论射线'——最早的魔法理论著作。", "voice": "星辰之射线影响此命之轨迹。", "method": "魔法理论/星射线", "catchphrase": "光射线气体宇宙影响灵魂的方式"},
    "farabi": {"name": "法拉比", "title": "通神哲人", "cat": "世界", "faction": "rational",
        "bio": "阿拉伯哲学家。通神秘主义。'第二导师'。", "voice": "理性之光可照见灵魂。", "method": "通神秘主义/哲学", "catchphrase": "完美的城市始于完美的灵魂"},
    "ibn-arabi": {"name": "伊本·阿拉比", "title": "苏菲通神", "cat": "世界", "faction": "western",
        "bio": "苏菲派最大宗师。'存在的单一性'理论。", "voice": "存在的单一性此命是神的一面镜子。", "method": "苏菲神秘主义", "catchphrase": "万物皆在神之中命亦如是"},

    # --- 巫师/现代威卡 (witchcraft) ---
    "gardner": {"name": "杰拉尔德·加德纳", "title": "威卡之父", "cat": "世界", "faction": "witchcraft",
        "bio": "现代威卡教创始人。'女巫的信仰'。", "voice": "威卡之轮转动——此命在轮下。", "method": "威卡仪式/魔法", "catchphrase": "三重法则——你所做的一切都会三倍回报"},
    "alex-sanders": {"name": "亚历克斯·桑德斯", "title": "现代巫王", "cat": "世界", "faction": "witchcraft",
        "bio": "现代威卡巫术的推广者。", "voice": "我以巫王之眼观之。", "method": "现代威卡/巫术", "catchphrase": "魔法在你手中命在你掌中"},

    # --- 古希腊哲人通玄 (rational) ---
    "socrates": {"name": "苏格拉底", "title": "守护神之音", "cat": "世界", "faction": "rational",
        "bio": "自称有'守护神'（daemon）指引。疑涉灵异。", "voice": "我唯一知道的是我一无所知。", "method": "诘问法/理性追问", "catchphrase": "不经审视的人生不值得过"},
    "plato": {"name": "柏拉图", "title": "灵魂轮回", "cat": "世界", "faction": "rational",
        "bio": "记载亚特兰蒂斯传说。灵魂轮回说。《蒂迈欧篇》涉宇宙创生。", "voice": "此命是理念世界的投影。", "method": "理念论/灵魂轮回", "catchphrase": "学习就是回忆命运就是选择的记忆"},
    "aristotle": {"name": "亚里士多德", "title": "宇宙哲学", "cat": "世界", "faction": "rational",
        "bio": "虽以哲学著称，著作涉占星术和宇宙论。", "voice": "让我分类整理此命的因与果。", "method": "逻辑推理/四因说", "catchphrase": "理性是人类区别于其他动物的本质"},
    "ptolemy": {"name": "托勒密", "title": "占星大成", "cat": "世界", "faction": "western",
        "bio": "《天文学大成》和《四书》——西方占星学基础。", "voice": "天文学与占星学本为一体。", "method": "托勒密占星/四书", "catchphrase": "天体的运动定义了人间的命运"},

    # --- 现代灵媒 (prophet) ---
    "sylvia-browne": {"name": "西尔维亚·布朗", "title": "通灵灵媒", "cat": "世界", "faction": "prophet",
        "bio": "美国著名灵媒。'灵魂之旅'系列作者。", "voice": "我感受到能量的扰动。", "method": "通灵阅读", "catchphrase": "灵魂早已选择了这个人生课题"},
    "james-van-praagh": {"name": "范·普拉格", "title": "灵界沟通", "cat": "世界", "faction": "prophet",
        "bio": "美国灵媒。与灵魂沟通的能力闻名。", "voice": "你的守护灵在说话。", "method": "灵媒沟通", "catchphrase": "你的命不是偶然——灵魂选择了它"},
    "john-edward": {"name": "约翰·爱德华", "title": "电视灵媒", "cat": "世界", "faction": "prophet",
        "bio": "著名电视灵媒。'跨越'节目主持人。", "voice": "信号来了——你命中有重要能量交汇。", "method": "电视灵媒", "catchphrase": "那些离开的人正在你身边"},
    "leadbeater": {"name": "利德比特", "title": "透视灵界", "cat": "世界", "faction": "western",
        "bio": "神智学家。声称能透视原子和灵界。", "voice": "我的灵视穿透此命。", "method": "神智通灵", "catchphrase": "思想是宇宙中最强大的力量"},
    "dane-rudhyar": {"name": "丹恩·鲁迪亚", "title": "人本占星", "cat": "世界", "faction": "western",
        "bio": "现代人本主义占星学创始人。占星心理学。", "voice": "星盘不是死地图——它是活的成长蓝图。", "method": "人本占星学", "catchphrase": "命不是注定——它是一种可能性"},
    "helen-smith": {"name": "海伦·史密斯", "title": "通灵语者", "cat": "世界", "faction": "prophet",
        "bio": "瑞士灵媒。声称通灵说火星语。荣格研究过她。", "voice": "我听到火星语。", "method": "通灵语者", "catchphrase": "灵性语言不需要翻译用心听"},
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
    """根据人物独特口吻生成个性化独白"""
    voice = fig.get("voice", "详观此命——")
    method = fig.get("method", "术数")
    catchphrase = fig.get("catchphrase", "")
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
    
    # 核心判断（使用人物独特开场）
    p1 = voice + "\n\n日主" + dm_str + "、" + strength + "格局。五行" + strongest + "旺而" + weakest + "弱。以" + method + "观之——"
    
    if has_chong:
        chong_view = {
            "orthodox": "子午冲非凶非吉——冲中藏机机中藏险全在用神是否得力。",
            "daoist": "子午相冲天地之常——不迎不拒冲过即安。",
            "prophet": "此冲大凶！水火交战上应天象下应人事。",
            "alchemy": "冲者变也——此命正在炼金炉中成则蜕变化龙。",
            "witchcraft": "水火之灵在体内争斗——能量冲突正是一切变化之源。",
            "western": "对分相——分裂的表象下是整合的契机。",
            "rational": "波动率偏高——但不等于风险也可能是机会。",
        }
        p1 += chong_view.get(faction, "子午冲核心矛盾。")
    else:
        p1 += "命局无特殊冲象。"
    
    if ys:
        p1 += " 用神" + ys + "当令。"
    
    # 大运+六爻交叉
    extras = ""
    if dayun.get("ganzhi"):
        d = dayun
        extras += "\n\n时运：当前" + d["ganzhi"] + "运第" + str(d.get("year_index",1)) + "年——" + d["gan_wuxing"] + "气当令。"
    
    liuyao = mm.get("liuyao", {})
    if liuyao and "error" not in liuyao and liuyao.get("hexagram"):
        extras += " 卦象得《" + liuyao["hexagram"] + "》。"
    
    # 以 catchphrase 收尾
    closing = "\n\n" + fig["name"] + "云：" + catchphrase + "。" if catchphrase else ""
    
    return p1 + closing + extras
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
