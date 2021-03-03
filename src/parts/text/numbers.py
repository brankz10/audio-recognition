# Copyright (c) 2017 Keith Ito
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" from https://github.com/keithito/tacotron 
Modifed to add support for time and slight tweaks to _expand_number
"""

import re

_unidade_to_text = {
    "0": "zero",
    "1": "um",
    "2": "dois",
    "3": "três",
    "4": "quatro",
    "5": "cinco",
    "6": "seis",
    "7": "sete",
    "8": "oito",
    "9": "nove",
    "10": "dez",
    "11": "onze",
    "12": "doze",
    "13": "treze",
    "14": "catorze",
    "15": "quinze",
    "16": "dezesseis",
    "17": "dezessete",
    "18": "dezoito",
    "19": "dezenove",
}

_dezena_to_text = {
    "2": "vinte",
    "3": "trinta",
    "4": "quarenta",
    "5": "cinquenta",
    "6": "sessenta",
    "7": "setenta",
    "8": "oitenta",
    "9": "noventa",
}

_centena_to_text = {
    "1": "cento",
    "2": "duzentos",
    "3": "trezentos",
    "4": "quatrocentos",
    "5": "quinhentos",
    "6": "seiscentos",
    "7": "setecentos",
    "8": "oitocentos",
    "9": "novecentos",
}

def _expand_dezena(m):
    if int(m) < 20:
        return _unidade_to_text.get(m)
    else:
        if int(m) % 10 == 0:
            return _dezena_to_text.get(str(int(m) // 10))
        else:
            return _dezena_to_text.get(str(int(m) // 10)) + " e " + _unidade_to_text.get(str(int(m) % 10))

def _expand_centena(m):
    if int(m) // 100 == 0:
        return _expand_dezena(str(int(m) % 100)) 
    else:
        if int(m) % 100 == 0:
            if int(m) == 100:
                return "cem"
            else:
                return _centena_to_text.get(str(int(m) // 100))
        else:
            return _centena_to_text.get(str(int(m) // 100)) + " e " + _expand_dezena(str(int(m) % 100))


def _expand_milhar(m):
    if int(m) >= 2000:
        if int(m) % 1000 != 0:
            if (int(m) % 1000 < 100) or ((int(m) % 1000) % 100 ==0):
                return _expand_centena(str(int(m) // 1000)) + " mil e " + _expand_centena(str(int(m) % 1000))
            else:
                return _expand_centena(str(int(m) // 1000)) + " mil " + _expand_centena(str(int(m) % 1000))
        else:
            return _expand_centena(str(int(m) // 1000)) + " mil"
    else:
        if int(m)//1000 == 0:
            return _centena_to_text.get(str(int(m) % 1000))
        elif int(m)//1000 == 1:
            if int(m) == 1000:
                return "mil"
            else:
                return "mil " + _expand_centena(str(int(m) % 1000))
            

def _expand_million(m):
    if int(m) >= 2000000:
        if int(m) % 1000000 != 0:
            return _expand_centena(str(int(m) // 1000000)) + " milhões " + _expand_milhar(str(int(m) % 1000000))
        else:
            return _expand_milhar(str(int(m) // 1000)) + " milhões"
    else:
        if int(m)//1000000 == 0:
            return _expand_milhar.get(str(int(m) % 1000000))
        elif int(m)//1000000 == 1:
            if int(m) == 1000000:
                return "um milhão"
            else:
                return "um milhão " + _expand_milhar(str(int(m) % 1000000))
            
def _expand_billion(m):
    if int(m) >= 2000000000:
        if int(m) % 1000000000 != 0:
            return _expand_centena(str(int(m) // 1000000000)) + " bilhões " + _expand_million(str(int(m) % 1000000000))
        else:
            return _expand_million(str(int(m) // 1000)) + " bilhões"
    else:
        if int(m)//1000000000 == 0:
            return _expand_million.get(str(int(m) % 1000000000))
        elif int(m)//1000000000 == 1:
            if int(m) == 1000000000:
                return "um bilhão"
            else:
                return "um bilhão " + _expand_million(str(int(m) % 1000000000))
            
def _expand_number(m):
    m = str(int(m.group(0)))
    if int(m) < 10:
        return _unidade_to_text.get(m)
    elif int(m) < 100:
        return _expand_dezena(m)
    elif int(m) < 1000:
        return _expand_centena(m)
    elif int(m) < 1000000:
        return _expand_milhar(m)
    elif int(m) < 1000000000:
        return _expand_million(m)
    elif int(m) < 1000000000000:
        return _expand_billion(m)


_comma_number_re = re.compile(r'([0-9][0-9\,]+[0-9])')
_decimal_number_re = re.compile(r'([0-9]+\.[0-9]+)')
_reais_re = re.compile(r'r\$([0-9\.\,]*[0-9]+)')
_number_re = re.compile(r'[0-9]+')


def _remove_commas(m):
    return m.group(1).replace('.', '')


def _expand_decimal_point(m):
    return m.group(1).replace(',', ' vírgula ')


def _expand_reais(m):
    match = m.group(1)
    parts = match.split(',')
    if len(parts) > 2:
        return match + ' reais'  # Unexpected format
    reais = int(parts[0]) if parts[0] else 0
    cents = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if reais and cents:
        real_unit = 'real' if reais == 1 else 'reais'
        cent_unit = 'centavo' if cents == 1 else 'centavos'
        return '%s %s, %s %s' % (reais, real_unit, cents, cent_unit)
    elif reais:
        real_unit = 'real' if reais == 1 else 'reais'
        return '%s %s' % (reais, real_unit)
    elif cents:
        cent_unit = 'centavo' if cents == 1 else 'centavos'
        return '%s %s' % (cents, cent_unit)
    else:
        return 'zero reais'


def normalize_numbers(text):
    text = re.sub(_comma_number_re, _remove_commas, text)
    text = re.sub(_reais_re, _expand_reais, text)
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = re.sub(_number_re, _expand_number, text)
    return text
