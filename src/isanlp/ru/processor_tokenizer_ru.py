#from ..en.processor_tokenizer_nltk_en import _en_abbrevs
from nltk.tokenize import RegexpTokenizer
import string
import re

from ..annotation import Token

_ru_abbrevs = [
    r'акад\.',
    r'б\.',
    r'вл\.',
    r'абл\.',
    r'абс\.',
    r'абх\.',
    r'авар\.',
    r'авг\.',
    r'австр\.',
    r'австрал\.',
    r'авт\.',
    r'агр\.',
    r'адж\.',
    r'адм\.',
    r'адыг\.',
    r'азерб\.',
    r'акад\.',
    r'акк\.',
    r'акц\.',
    r'алб\.',
    r'алг\.',
    r'алж\.',
    r'алт\.',
    r'алф\.',
    r'альм\.',
    r'альп\.',
    r'амер\.',
    r'анат\.',
    r'англ\.',
    r'ангол\.',
    r'аннот\.',
    r'антич\.',
    r'ап\.',
    r'апр\.',
    r'арам\.',
    r'аргент\.',
    r'арифм\.',
    r'арт\.',
    r'архип\.',
    r'архим\.',
    r'асср',
    r'асс\.',
    r'ассир\.',
    r'астр\.',
    r'ат\.',
    r'атм\.',
    r'афг\.',
    r'афр\.',
    r'балк\.',
    r'балт\.',
    r'башк\.',
    r'безв\.',
    r'безл\.',
    r'бельг\.',
    r'библ\.',
    r'биогр\.',
    r'биол\.',
    r'бирм\.',
    r'бол\.',
    r'болг\.',
    r'буд\.',
    r'бюдж\.',
    r'бюлл\.',
    r'вал\.',
    r'вв\.',
    r'вдхр\.',
    r'вед\.',
    r'вел\.',
    r'венг\.',
    r'вкл\.',
    r'внеш\.',
    r'внутр\.',
    r'вод\. ст\.',
    r'воен\.',
    r'возв\.',
    r'возд\.',
    r'воскр\.',
    r'вост\.',
    r'вт\.',
    r'вьетн\.',
    r'г\.',
    r'гг\.',
    r'га\.',
    r'гав\.',
    r'газ\.',
    r'гвин\.',
    r'гВт\.',
    r'ГГц\.',
    r'ген\.',
    r'ген\. л\.',
    r'ген\. м\.',
    r'ген\. п\.',
    r'геогр\.',
    r'геод\.',
    r'геол\.',
    r'геом\.',
    r'герм\.',
    r'г-жа\.',
    r'гл\.',
    r'гор\.',
    r'гос\.',
    r'госп\.',
    r'град\.',
    r'греч\.',
    r'гр\.',
    r'гражд\.',
    r'греч\.',
    r'груз\.',
    r'губ\.',
    r'Гц\.',
    r'ГэВ\.',
    r'дптр\.',
    r'д\. б\. н\.',
    r'Д\. В\.',
    r'д\. г\. н\.',
    r'д\. г\. м\. н\.',
    r'д\.б\.н\.',
    r'Д\.В\.',
    r'д\.г\.н\.',
    r'д\.г\.м\.н\.',
    r'дер\.',
    r'д\. и\. н\.',
    r'д\. иск\.',
    r'д\. м\. н\.',
    r'д\. н\.',
    r'д\. о\.',
    r'д\. п\.',
    r'д\. т\. н\.',
    r'д\. ф\. н\.',
    r'д\. ф\. м\. н\.',
    r'д\. х\. н\.',
    r'д\. ч\.',
    r'д\.и\.н\.',
    r'д\.иск\.',
    r'д\.м\.н\.',
    r'д\.н\.',
    r'д\.о\.',
    r'д\.п\.',
    r'д\.т\.н\.',
    r'д\.ф\.н\.',
    r'д\.ф\-м\.н\.',
    r'д\.х\.н\.',
    r'д\.ч\.',
    r'дБ\.',
    r'деепр\.',
    r'действ\.',
    r'дек\.',
    r'дер\.',
    r'Дж\.',
    r'диак\.',
    r'диал\.',
    r'диал\.',
    r'диам\.',
    r'див\.',
    r'диз\.',
    r'дир\.',
    r'дисс\.',
    r'дист\.',
    r'дифф\.',
    r'дкг\.',
    r'дкл\.',
    r'дкм\.',
    r'дм\.',
    r'доб\.',
    r'док\.',
    r'докт\.',
    r'долл\.',
    r'доп\.',
    r'доц\.',
    r'драм\.',
    r'дубл\.',
    r'евр\.',
    r'европ\.',
    r'егип\.',
    r'ед\.',
    r'ед\. ч\.',
    r'ед\.ч\.',
    r'ежедн\.',
    r'ежемес\.',
    r'еженед\.',
    r'ефр\.',
    r'ж\.',
    r'ж\. д\.',
    r'жен\.',
    r'жит\.',
    r'женск\.',
    r'журн\.',
    r'засл\. арт\.',
    r'з\. д\.',
    r'зав\. хоз\.',
    r'зав\.',
    r'загл\.',
    r'зал\.',
    r'зам\.',
    r'заруб\.',
    r'зем\.',
    r'зол\.',
    r'др\.',
    r'пр\.',
    r'и\. о\.',
    r'игум\.',
    r'иером\.',
    r'им\.',
    r'иностр\.',
    r'инд\.',
    r'индонез\.',
    r'итал\.',
    r'канд\.',
    r'коп\.',
    r'корп\.',
    r'кв\.',
    r'ква\.',
    r'квт\.',
    r'к\. м\. н\.',
    r'к\. х\. н\.',
    r'к\. т\. н\.',
    r'к\.м\.н\.',
    r'к\.х\.н\.',
    r'к\.т\.н\.',
    r'к\. ф\.-м\. н\.',
    r'кг\.',
    r'кгс\.',
    r'кгц\.',
    r'кд\.',
    r'кдж\.',
    r'кирг\.',
    r'ккал\.',
    r'кл\.',
    r'км\.',
    r'кмоль\.',
    r'книжн\.',
    r'кэв\.',
    r'л\.с\.',
    r'лаб\.',
    r'лат\.',
    r'латв\.',
    r'лейт\.',
    r'лит\.',
    r'м\.',
    r'мин\.',
    r'м­р\.',
    r'муж\.',
    r'м\.н\.с\.',
    r'макс\.',
    r'матем\.',
    r'мат\.',
    r'маш\.',
    r'м-во\.',
    r'мгц\.',
    r'мдж\.',
    r'мед\.',
    r'мес\.',
    r'мин-во\.',
    r'митр\.',
    r'мка\.',
    r'мкал\.',
    r'мкв\.',
    r'мквт\.',
    r'мкм\.',
    r'мкмк\.',
    r'мком\.',
    r'мкпа\.',
    r'мкр\.',
    r'мкф\.',
    r'мкюри\.',
    r'мл\.',
    r'млк\.',
    r'млн\.',
    r'млрд\.',
    r'мн\.ч\.',
    r'моск\.',
    r'мпа\.',
    r'мс\.',
    r'мужск\.',
    r'мэв\.',
    r'н\.э\.',
    r'нем\.',
    r'обл\.',
    r'пос\.',
    r'пер\.',
    r'пр\.',
    r'пл\.',
    r'р\.',
    r'рис\.',
    r'стр\.',
    r'сокр\.',
    r'ст\.н\.с\.',
    r'ст\.',
    r'т\.',
    r'т\. ?д\.',
    r'т\. ?е\.',
    r'т\. ?к\.',
    r'т\. ?н\.',
    r'т\. ?о\.',
    r'т\. ?п\.',
    r'т\. ?с\.',
    r'тыс\.',
    r'тел\.',
    r'тов\.',
    r'трлн\.',
    r'ул\.',
    r'франц\.',
    r'ч\.',
    r'чел\.',
    r'\d?\d\.\d\d\.\d\d(?:\d\d)',
    r'\w\.\w\.'
]

_ru_rules = [u'[-\w.]+@(?:[A-z0-9][-A-z0-9]+\.)+[A-z]{2,4}', #e-mail
         u'(?:[01]?[0-9]|2[0-4]):[0-5][0-9]', # times
         u'(?:mailto:|(?:news|http|https|ftp|ftps)://)[\w\.\-]+|^(?:www(?:\.[\w\-]+)+)', # urls
         u'(http[s]?:\/\/)?([^\/\s]+\/)(.*)(?:com|org|net|html)',
         u'--',
         u'\.\.\.',
         u'\d+\.\d+',
         u'[' + string.punctuation + u']',
         u'[а-яА-ЯёЁa-zA-Z0-9]+',
         u'\S']


#_ru_regex = u'|'.join(_ru_abbrevs + _en_abbrevs + _ru_rules)
_ru_regex = u'|'.join(_ru_abbrevs + _ru_rules)


class ProcessorTokenizerRu:
    """Performs tokenization of Russian texts with regexes.
    
    Wrapper around NLTK RegexpTokenizer. Supports Russian abbreviations.
    """
    
    def __init__(self, delay_init = False):
        self._proc = None
        if not delay_init:
            self.init()


    def init(self):
        if self._proc is None:
            self._proc = RegexpTokenizer(_ru_regex, flags=re.IGNORECASE)


    def __call__(self, text):
        assert self._proc
        return [Token(text[start : end], start, end) for (start, end) in self._proc.span_tokenize(text)]
    
