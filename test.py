# 可变长度的DNA加密

def unicode_to_dna(unicode_string):
    symbols = ["A", "G", "C", "T"]
    result = []
    
    # 计算需要的DNA长度
    max_code_point = max(ord(char) for char in unicode_string)
    length = (max_code_point.bit_length() + 1) // 2  # 计算所需长度

    for char in unicode_string:
        code_point = ord(char)
        dna_representation = ''
        
        # 将code_point转为DNA表示
        for i in range(length):
            # 取最低两位
            dna_representation = symbols[code_point & 3] + dna_representation
            code_point >>= 2  # 右移两位
            
        result.append(dna_representation)

    return result

def dna_to_unicode(dna_list):
    symbols = ["A", "G", "C", "T"]
    result = []
    
    for dna in dna_list:
        code_point = 0
        
        # 将DNA表示转换回Unicode码点
        for i, char in enumerate(reversed(dna)):
            code_point += symbols.index(char) << (2 * i)  # 每个字符占用2位
        
        result.append(chr(code_point))  # 转回Unicode字符

    return ''.join(result)

def get_individual_dna_length(unicode_string):
    # 每个Unicode字符的DNA表示长度
    max_code_point = max(ord(char) for char in unicode_string)
    dna_length = (max_code_point.bit_length() + 1) // 2  # 计算所需的DNA长度
    return dna_length


if __name__ == "__main__":
    unicode_string = input()
    dna_list = unicode_to_dna(unicode_string)
    length = get_individual_dna_length(unicode_string)
    print(length)
    print(" ".join(dna_list))
    print(dna_to_unicode(dna_list))
