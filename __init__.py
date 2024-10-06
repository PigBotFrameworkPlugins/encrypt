from pbf.utils import MetaData
from pbf.utils.Config import Config
from pbf.utils.Register import Command
from pbf.setup import logger, pluginsManager
from pbf import config as defaultConfig
from pbf.controller.Data import Event
from pbf.controller.Client import Msg
from pbf.statement import Statement

class FaceStatement(Statement):
    cqtype: str = "face"
    id: str = None

    def __init__(self, id: str):
        self.id = str(id)


class MyConfig(Config):
    originData = {
        "owner_id": 114514
    }
config = MyConfig(defaultConfig.plugins_config.get("GroupManagement", {}))


def checkBanwords(event: Event):
    if not pluginsManager.hasApi("banwords"):
        Msg("本插件需要Banwords前置插件！", event=event).send()
        return False
    return True


meta_data = MetaData(
    name="加解密",
    version="0.0.1",
    versionCode=1,
    description="加解密插件",
    author="XzyStudio",
    license="MIT",
    keywords=["pbf", "plugin", "encrypt"],
    readme="""
# 加解密插件
encrypt插件提供了一些加解密的功能。
    """
)


class UnicodeDNAConverter:
    def __init__(self, fixed_length=11):
        self.fixed_length = fixed_length
        self.symbols = ["A", "G", "C", "T"]

    def unicode_to_dna_fixed_length(self, unicode_string):
        result = []
        
        for char in unicode_string:
            code_point = ord(char)
            dna_representation = ['A'] * self.fixed_length  # 初始化固定长度的DNA序列
            
            # 将code_point转为DNA表示
            for i in range(self.fixed_length):
                dna_representation[self.fixed_length - 1 - i] = self.symbols[code_point & 3]
                code_point >>= 2
            
            result.append(''.join(dna_representation))

        return result

    def dna_to_unicode_fixed_length(self, dna_list):
        result = []
        
        for dna in dna_list:
            code_point = 0
            
            # 将DNA表示转换回Unicode码点
            for i, char in enumerate(dna):
                code_point += self.symbols.index(char) << (2 * (len(dna) - 1 - i))
            
            result.append(chr(code_point))  # 转回Unicode字符

        return ''.join(result)

    def get_individual_dna_length(self, unicode_string):
        # 每个Unicode字符的DNA表示长度
        max_code_point = max(ord(char) for char in unicode_string)
        dna_length = (max_code_point.bit_length() + 1) // 2  # 计算所需的DNA长度
        return dna_length
    
    def encode(self, unicode_string):
        dataList: list = self.unicode_to_dna_fixed_length(unicode_string)
        s: str = "".join(dataList)
        s = " ".join([s[i:i+3] for i in range(0, len(s), 3)])
        if len(s.split()[-1]) < 3:
            s += "=" * (3 - len(s.split()[-1]))
        return s
    
    def decode(self, dna_string):
        dna_string = dna_string.replace(" ", "").replace("=", "")
        dna_list = [dna_string[i:i+self.fixed_length] for i in range(0, len(dna_string), self.fixed_length)]
        return self.dna_to_unicode_fixed_length(dna_list)


# 兽音译者，一种将“呜嗷啊~”四个字符，通过特殊算法，将明文进行重新组合的加密算法。一种新的咆哮体加密算法。还可以将四个字符任意换成其它的字符，进行加密。
# 另，可下载油猴插件Google selected text translator，https://greasyfork.org/en/scripts/36842-google-select-text-translator
# 该插件经设置后，不仅可以划词翻译兽音密文，也可生成兽音密文
class HowlingAnimalsTranslator:
    __animalVoice = "嗷呜啊~"

    def __init__(self, newAnimalVoice=None):
        self.setAnimalVoice(newAnimalVoice)

    def convert(self, txt=""):
        txt = txt.strip()
        if (txt.__len__() < 1):
            return ""
        result = self.__animalVoice[3] + self.__animalVoice[1] + self.__animalVoice[0]
        offset = 0
        for t in txt:
            c = ord(t)
            b = 12
            while (b >= 0):
                hex = (c >> b) + offset & 15
                offset += 1
                result += self.__animalVoice[int(hex >> 2)]
                result += self.__animalVoice[int(hex & 3)]
                b -= 4
        result += self.__animalVoice[2]
        return result

    def deConvert(self, txt):
        txt = txt.strip()
        if (not self.identify(txt)):
            return "Incorrect format!"
        result = ""
        i = 3
        offset = 0
        while (i < txt.__len__() - 1):
            c = 0
            b = i + 8
            while (i < b):
                n1 = self.__animalVoice.index(txt[i])
                i += 1
                n2 = self.__animalVoice.index(txt[i])
                c = c << 4 | ((n1 << 2 | n2) + offset) & 15
                if (offset == 0):
                    offset = 0x10000 * 0x10000 - 1
                else:
                    offset -= 1
                i += 1
            result += chr(c)
        return result

    def identify(self, txt):
        if (txt):
            txt = txt.strip()
            if (txt.__len__() > 11):
                if (txt[0] == self.__animalVoice[3] and txt[1] == self.__animalVoice[1] and txt[2] ==
                        self.__animalVoice[0] and txt[-1] == self.__animalVoice[2] and ((txt.__len__() - 4) % 8) == 0):
                    for t in txt:
                        if (not self.__animalVoice.__contains__(t)):
                            return False
                    return True
        return False

    def setAnimalVoice(self, voiceTxt):
        if (voiceTxt):
            voiceTxt = voiceTxt.strip()
            if (voiceTxt.__len__() == 4):
                self.__animalVoice = voiceTxt
                return True
        return False

    def getAnimalVoice(self):
        return self.__animalVoice


class Api:
    unicodeDNAConverter = UnicodeDNAConverter()
    howlingAnimalsTranslator = HowlingAnimalsTranslator()

@Command(
    name="密码子加密",
    usage="密码子加密 <原文>",
    description="将Unicode字符串转换为DNA序列",
    permission=checkBanwords
)
def unicode_to_dna(event: Event):
    msg: str = event.raw_message.replace("密码子加密", "").strip()
    if pluginsManager.require("banwords").check(msg).get("result"):
        Msg([
            FaceStatement(1), " 403 Forbidden\n",
            "消息包含违禁词，这是一片深不可测的深渊...", "\n"
        ], event=event).send()
        return
    result = Api.unicodeDNAConverter.encode(msg)
    Msg([
        FaceStatement(1), " 200 OK\n",
        "加密结果：", result, "\n"
    ], event=event).send()

@Command(
    name="密码子解密",
    usage="密码子解密 <密文>",
    description="将DNA序列转换为Unicode字符串",
    permission=checkBanwords
)
def dna_to_unicode(event: Event):
    msg: str = event.raw_message.replace("密码子解密", "").strip()
    result = Api.unicodeDNAConverter.decode(msg)
    if pluginsManager.require("banwords").check(result).get("result"):
        Msg([
            FaceStatement(1), " 403 Forbidden\n",
            "消息包含违禁词，这是一片深不可测的深渊...", "\n"
        ], event=event).send()
        return
    Msg([
        FaceStatement(1), " 200 OK\n",
        "解密结果：", result, "\n"
    ], event=event).send()

@Command(
    name="兽音加密",
    usage="兽音加密 <原文>",
    description="将明文转换为兽音密文",
    permission=checkBanwords
)
def howling_animals_encrypt(event: Event):
    msg: str = event.raw_message.replace("兽音加密", "").strip()
    if pluginsManager.require("banwords").check(msg).get("result"):
        Msg([
            FaceStatement(1), " 403 Forbidden\n",
            "消息包含违禁词，这是一片深不可测的深渊...", "\n"
        ], event=event).send()
        return
    result = Api.howlingAnimalsTranslator.convert(msg)
    Msg([
        FaceStatement(1), " 200 OK\n",
        "加密结果：", result, "\n"
    ], event=event).send()

@Command(
    name="兽音解密",
    usage="兽音解密 <密文>",
    description="将兽音密文转换为明文",
    permission=checkBanwords
)
def howling_animals_decrypt(event: Event):
    msg: str = event.raw_message.replace("兽音解密", "").strip()
    result = Api.howlingAnimalsTranslator.deConvert(msg)
    if pluginsManager.require("banwords").check(result).get("result"):
        Msg([
            FaceStatement(1), " 403 Forbidden\n",
            "消息包含违禁词，这是一片深不可测的深渊...", "\n"
        ], event=event).send()
        return
    Msg([
        FaceStatement(1), " 200 OK\n",
        "解密结果：", result, "\n"
    ], event=event).send()
