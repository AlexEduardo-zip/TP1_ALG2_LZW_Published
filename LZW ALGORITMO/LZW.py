import sys
import os
import json
import time

class CompactTrie:
    def __init__(self):
        self.trie = {}
        self.codes = {}
        self.size = 0

    def insert(self, binary_str, code):
        node = self.trie
        for bit in binary_str:
            if bit not in node:
                node[bit] = {}
            node = node[bit]
        node['code'] = code
        self.codes[binary_str] = code
        self.size += 1

    def search(self, binary_str):
        node = self.trie
        for bit in binary_str:
            if bit not in node:
                return None
            node = node[bit]
        return node.get('code', None)

def collect_statistics(stats, event, value):
    if event not in stats:
        stats[event] = []
    stats[event].append(value)

def compress_with_compact_trie_debug(text, bit_limit, stats):
    trie = CompactTrie()
    max_table_size = 2 ** bit_limit
    next_code = 256

    for i in range(256):
        trie.insert(format(i, "08b"), i)

    current_string = ""
    compressed_output = []

    for symbol in text:
        binary_symbol = format(ord(symbol), "08b")
        combined_string = current_string + binary_symbol

        if trie.search(combined_string) is not None:
            current_string = combined_string
        else:
            code = trie.search(current_string)
            if code is None:
                raise ValueError(f"Erro: string não encontrada na Trie ({current_string})")

            compressed_output.append(code)
            current_string = binary_symbol

            if next_code < max_table_size:
                trie.insert(combined_string, next_code)
                next_code += 1

        # Coleta de estatísticas a cada passo
        collect_statistics(stats, 'compressed_output', len(compressed_output))
        collect_statistics(stats, 'trie_size', trie.size)

    if current_string:
        code = trie.search(current_string)
        if code is None:
            raise ValueError(f"Erro: string final não encontrada na Trie ({current_string})")
        compressed_output.append(code)
        collect_statistics(stats, 'compressed_output', len(compressed_output))
        collect_statistics(stats, 'trie_size', trie.size)

    return compressed_output

def decompress_with_compact_trie(compressed_data, bit_limit, stats):
    max_table_size = 2 ** bit_limit
    next_code = 256
    reverse_map = {i: chr(i) for i in range(256)}

    current_code = compressed_data.pop(0)
    current_string = reverse_map[current_code]
    decompressed_output = [current_string]

    for code in compressed_data:
        if code in reverse_map:
            entry = reverse_map[code]
        elif code == next_code:
            entry = current_string + current_string[0]
        else:
            raise ValueError(f"Erro na descompressão: código inválido ({code}).")

        decompressed_output.append(entry)
        collect_statistics(stats, 'decompressed_output', len(decompressed_output))

        if next_code < max_table_size:
            new_entry = current_string + entry[0]
            reverse_map[next_code] = new_entry
            next_code += 1

        current_string = entry

    return "".join(decompressed_output)

def compress_with_variable_size(text, initial_bit_limit, max_bit_limit, stats):
    trie = CompactTrie()
    next_code = 256
    current_bit_limit = initial_bit_limit
    max_table_size = 2 ** current_bit_limit

    for i in range(256):
        trie.insert(format(i, "08b"), i)

    current_string = ""
    compressed_output = []

    for symbol in text:
        binary_symbol = format(ord(symbol), "08b")
        combined_string = current_string + binary_symbol

        if trie.search(combined_string) is not None:
            current_string = combined_string
        else:
            code = trie.search(current_string)
            if code is None:
                raise ValueError(f"Erro: string não encontrada na Trie ({current_string})")

            compressed_output.append(code)

            if next_code < max_table_size:
                trie.insert(combined_string, next_code)
                next_code += 1

                if next_code >= max_table_size and current_bit_limit < max_bit_limit:
                    current_bit_limit += 1
                    max_table_size = 2 ** current_bit_limit

            current_string = binary_symbol

        collect_statistics(stats, 'compressed_output', len(compressed_output))
        collect_statistics(stats, 'trie_size', trie.size)

    if current_string:
        code = trie.search(current_string)
        if code is None:
            raise ValueError(f"Erro: string final não encontrada na Trie ({current_string})")
        compressed_output.append(code)
        collect_statistics(stats, 'compressed_output', len(compressed_output))

    return compressed_output, current_bit_limit

def decompress_with_variable_size(compressed_data, initial_bit_limit, max_bit_limit, stats):
    current_bit_limit = initial_bit_limit
    max_table_size = 2 ** current_bit_limit
    next_code = 256
    reverse_map = {i: chr(i) for i in range(256)}

    current_code = compressed_data.pop(0)
    current_string = reverse_map[current_code]
    decompressed_output = [current_string]

    for code in compressed_data:
        if code in reverse_map:
            entry = reverse_map[code]
        elif code == next_code:
            entry = current_string + current_string[0]
        else:
            raise ValueError(f"Erro na descompressão: código inválido ({code}).")

        decompressed_output.append(entry)
        collect_statistics(stats, 'decompressed_output', len(decompressed_output))

        if next_code < max_table_size:
            new_entry = current_string + entry[0]
            reverse_map[next_code] = new_entry
            next_code += 1

            if next_code >= max_table_size and current_bit_limit < max_bit_limit:
                current_bit_limit += 1
                max_table_size = 2 ** current_bit_limit

        current_string = entry

    return "".join(decompressed_output)

def filter_valid_characters(text, valid_characters):
    return ''.join(c for c in text if c in valid_characters)

def binary_to_string(data):
    return ''.join(chr(byte) for byte in data)

def string_to_binary(text):
    return bytes(ord(char) for char in text)

def compress_file_fixed_size_text(input_file, output_file, bit_limit, valid_characters, stats):
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    text = filter_valid_characters(text, valid_characters)

    start_time = time.time()
    compressed_data = compress_with_compact_trie_debug(text, bit_limit, stats)
    end_time = time.time()

    with open(output_file, 'wb') as file:
        for code in compressed_data:
            file.write(code.to_bytes((bit_limit + 7) // 8, byteorder='big'))

    stats['compression_time'] = end_time - start_time
    stats['original_size'] = os.path.getsize(input_file)
    stats['compressed_size'] = os.path.getsize(output_file)

def decompress_file_fixed_size_text(input_file, output_file, bit_limit, stats):
    with open(input_file, 'rb') as file:
        compressed_data = []
        while byte := file.read((bit_limit + 7) // 8):
            compressed_data.append(int.from_bytes(byte, byteorder='big'))

    start_time = time.time()
    decompressed_text = decompress_with_compact_trie(compressed_data, bit_limit, stats)
    end_time = time.time()

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(decompressed_text)

    stats['decompression_time'] = end_time - start_time

def compress_file_fixed_size_binary(input_file, output_file, bit_limit, stats):
    with open(input_file, 'rb') as file:
        data = file.read()

    text = binary_to_string(data)

    start_time = time.time()
    compressed_data = compress_with_compact_trie_debug(text, bit_limit, stats)
    end_time = time.time()

    with open(output_file, 'wb') as file:
        for code in compressed_data:
            file.write(code.to_bytes((bit_limit + 7) // 8, byteorder='big'))

    stats['compression_time'] = end_time - start_time
    stats['original_size'] = os.path.getsize(input_file)
    stats['compressed_size'] = os.path.getsize(output_file)

def decompress_file_fixed_size_binary(input_file, output_file, bit_limit, stats):
    with open(input_file, 'rb') as file:
        compressed_data = []
        while byte := file.read((bit_limit + 7) // 8):
            compressed_data.append(int.from_bytes(byte, byteorder='big'))

    start_time = time.time()
    decompressed_text = decompress_with_compact_trie(compressed_data, bit_limit, stats)
    end_time = time.time()

    decompressed_data = string_to_binary(decompressed_text)

    with open(output_file, 'wb') as file:
        file.write(decompressed_data)

    stats['decompression_time'] = end_time - start_time

def compress_file_variable_size_text(input_file, output_file, initial_bit_limit, max_bit_limit, valid_characters, stats):
    with open(input_file, 'r', encoding='utf-8') as file:
        text = file.read()

    text = filter_valid_characters(text, valid_characters)

    start_time = time.time()
    compressed_data, final_bit_limit = compress_with_variable_size(text, initial_bit_limit, max_bit_limit, stats)
    end_time = time.time()

    with open(output_file, 'wb') as file:
        for code in compressed_data:
            file.write(code.to_bytes((final_bit_limit + 7) // 8, byteorder='big'))

    stats['compression_time'] = end_time - start_time
    stats['original_size'] = os.path.getsize(input_file)
    stats['compressed_size'] = os.path.getsize(output_file)

def decompress_file_variable_size_text(input_file, output_file, initial_bit_limit, max_bit_limit, stats):
    with open(input_file, 'rb') as file:
        compressed_data = []
        while byte := file.read((max_bit_limit + 7) // 8):
            compressed_data.append(int.from_bytes(byte, byteorder='big'))

    start_time = time.time()
    decompressed_text = decompress_with_variable_size(compressed_data, initial_bit_limit, max_bit_limit, stats)
    end_time = time.time()

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(decompressed_text)

    stats['decompression_time'] = end_time - start_time

def compress_file_variable_size_binary(input_file, output_file, initial_bit_limit, max_bit_limit, stats):
    with open(input_file, 'rb') as file:
        data = file.read()

    text = binary_to_string(data)

    start_time = time.time()
    compressed_data, final_bit_limit = compress_with_variable_size(text, initial_bit_limit, max_bit_limit, stats)
    end_time = time.time()

    with open(output_file, 'wb') as file:
        for code in compressed_data:
            file.write(code.to_bytes((final_bit_limit + 7) // 8, byteorder='big'))

    stats['compression_time'] = end_time - start_time
    stats['original_size'] = os.path.getsize(input_file)
    stats['compressed_size'] = os.path.getsize(output_file)

def decompress_file_variable_size_binary(input_file, output_file, initial_bit_limit, max_bit_limit, stats):
    with open(input_file, 'rb') as file:
        compressed_data = []
        while byte := file.read((max_bit_limit + 7) // 8):
            compressed_data.append(int.from_bytes(byte, byteorder='big'))

    start_time = time.time()
    decompressed_text = decompress_with_variable_size(compressed_data, initial_bit_limit, max_bit_limit, stats)
    end_time = time.time()

    decompressed_data = string_to_binary(decompressed_text)

    with open(output_file, 'wb') as file:
        file.write(decompressed_data)

    stats['decompression_time'] = end_time - start_time

def main():
    if len(sys.argv) < 3:
        print("Uso: LZW.py <arquivo_de_entrada> <arquivo_de_saida> [<tamanho_inicial_de_bits> <tamanho_max_de_bits>]")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    file_extension = os.path.splitext(input_file)[1].lower()

    valid_characters = set(chr(i) for i in range(256))
    stats = {}

    if len(sys.argv) == 3:
        bit_limit = 12
        if file_extension == '.txt':
            compress_file_fixed_size_text(input_file, output_file, bit_limit, valid_characters, stats)
            decompress_file_fixed_size_text(output_file, 'decompressed.txt', bit_limit, stats)
        else:
            compress_file_fixed_size_binary(input_file, output_file, bit_limit, stats)
            decompress_file_fixed_size_binary(output_file, 'decompressed' + file_extension, bit_limit, stats)
    elif len(sys.argv) == 5:
        initial_bit_limit = int(sys.argv[3])
        max_bit_limit = int(sys.argv[4])
        if file_extension == '.txt':
            compress_file_variable_size_text(input_file, output_file, initial_bit_limit, max_bit_limit, valid_characters, stats)
            decompress_file_variable_size_text(output_file, 'decompressed.txt', initial_bit_limit, max_bit_limit, stats)
        else:
            compress_file_variable_size_binary(input_file, output_file, initial_bit_limit, max_bit_limit, stats)
            decompress_file_variable_size_binary(output_file, 'decompressed' + file_extension, initial_bit_limit, max_bit_limit, stats)
    else:
        print("Uso: LZW.py <arquivo_de_entrada> <arquivo_de_saida> [<tamanho_inicial_de_bits> <tamanho_max_de_bits>]")

    with open('stats.json', 'w') as stats_file:
        json.dump(stats, stats_file, indent=4)

if __name__ == "__main__":
    main()