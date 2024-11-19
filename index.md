---
title: TP1_ALG2_LZW
layout: home
---

# TP1_ALG2: Implementação do Algoritmo LZW

* TOC
{:toc}

Este projeto apresenta uma implementação detalhada do algoritmo de compressão LZW (Lempel-Ziv-Welch). Ele utiliza estruturas de dados eficientes, como uma árvore trie compacta, para armazenar as sequências de bits de forma otimizada. A implementação suporta compressão e descompressão tanto de arquivos de texto (`.txt`) quanto de arquivos binários (`.bmp`), permitindo a escolha entre tamanhos de código fixos e variáveis.

## Funcionalidades

- **Compressão de arquivos**: Transforma dados brutos em uma sequência compacta de códigos, reduzindo o tamanho do arquivo.
- **Descompressão de arquivos**: Restaura o conteúdo original a partir dos códigos gerados na compressão.
- **Árvore Trie Compacta**: Armazena as sequências binárias de maneira eficiente para operações rápidas de busca e inserção.
- **Tamanhos de código fixos e variáveis**: Permite um controle flexível da profundidade e complexidade da compressão.

## Como Utilizar

### Requisitos

- Python 3.x

### Execução

A execução do script é realizada via linha de comando. A estrutura geral do comando é:

```sh
python LZW.py <arquivo_de_entrada> <arquivo_de_saida> [<tamanho_inicial_de_bits> <tamanho_max_de_bits>]
```

#### Exemplos:

1. **Compressão de texto com tamanho de código fixo**:

```sh
python LZW.py pg18982.txt compressed.bin
```

2. **Compressão de texto com tamanho de código variável**:

```sh
python LZW.py pg18982.txt compressed.bin 9 16
```

3. **Compressão de imagem binária com tamanho de código fixo**:

```sh
python LZW.py imagem.bmp compressed.bin
```

4. **Compressão de imagem binária com tamanho de código variável**:

```sh
python LZW.py imagem.bmp compressed.bin 9 16
```

---

## Estrutura e Decisões do Projeto

### 1. **Árvore Trie Compacta**

A árvore trie compacta é uma estrutura hierárquica onde cada caminho de nós representa uma sequência de bits. Essa estrutura é crucial para o LZW, pois permite:

- **Inserção eficiente** de sequências durante a compressão.
- **Busca rápida** para verificar se uma sequência já está no dicionário.
- **Eliminação controlada** de sequências antigas (apenas para tamanhos de código variável).

#### Implementação da Trie Compacta

```Python
class CompactTrie:
    def __init__(self):
        self.trie = {}  # Representa os nós da árvore
        self.codes = {}  # Armazena a relação entre sequências e códigos

    def insert(self, binary_str, code):
        """
        Insere uma sequência binária como string, associando-a a um código único.
        """
        node = self.trie
        for bit in binary_str:
            if bit not in node:
                node[bit] = {}
            node = node[bit]
        node['code'] = code  # Armazena o código no nó final
        self.codes[binary_str] = code

    def search(self, binary_str):
        """
        Busca uma sequência binária na árvore e retorna o código associado, se existir.
        """
        node = self.trie
        for bit in binary_str:
            if bit not in node:
                return None  # Sequência não encontrada
            node = node[bit]
        return node.get('code', None)

    def delete(self, binary_str):
        """
        Remove uma sequência binária da árvore, mantendo a estrutura correta.
        """
        def _delete(node, binary_str, depth):
            if depth == len(binary_str):
                if 'code' in node:
                    del node['code']
                    return len(node) == 0
                return False
            bit = binary_str[depth]
            if bit in node and _delete(node[bit], binary_str, depth + 1):
                del node[bit]
                return len(node) == 0
            return False

        if binary_str in self.codes:
            _delete(self.trie, binary_str, 0)
            del self.codes[binary_str]
```

### 2. **Conversão de Dados Binários**

Arquivos binários contêm informações em formato bruto que não podem ser manipuladas diretamente como texto. Por isso, utilizamos funções para converter entre binário e string:

```Python
def binary_to_string(data):
    """
    Converte dados binários em uma sequência de caracteres.
    """
    return ''.join(chr(byte) for byte in data)

def string_to_binary(text):
    """
    Converte uma string de texto em dados binários.
    """
    return bytes(ord(char) for char in text)
```

Essa abordagem permite que tanto arquivos `.txt` quanto `.bmp` sejam processados de forma uniforme.

---

### 3. **Compressão com Tamanho Variável**

O tamanho variável dos códigos é uma técnica avançada que melhora a eficiência. Ele começa com um limite inferior (ex.: 9 bits) e expande gradualmente até um limite superior (ex.: 16 bits). Quando o dicionário atinge sua capacidade máxima, ele expande os códigos ou reinicia.

#### Funcionamento

1. **Inicialização do dicionário**:
   - Todos os caracteres ASCII (0-255) são mapeados para seus valores binários.

2. **Processamento da entrada**:
   - Verifica-se se uma sequência está no dicionário.
   - Se não estiver, adiciona-se a sequência ao dicionário e emite o código correspondente à parte já reconhecida.

3. **Expansão de tamanho**:
   - Quando o próximo código excede o limite atual, o número de bits é aumentado.

#### Implementação

```Python
def compress_with_variable_size(text, initial_bit_limit, max_bit_limit):
    trie = CompactTrie()
    next_code = 256
    current_bit_limit = initial_bit_limit
    max_table_size = 2 ** current_bit_limit

    # Inicializa o dicionário com caracteres ASCII
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
            compressed_output.append(code)

            if next_code < max_table_size:
                trie.insert(combined_string, next_code)
                next_code += 1

                # Expansão do limite de bits
                if next_code >= max_table_size and current_bit_limit < max_bit_limit:
                    current_bit_limit += 1
                    max_table_size = 2 ** current_bit_limit

            current_string = binary_symbol

    # Finaliza o processamento da última sequência
    if current_string:
        code = trie.search(current_string)
        compressed_output.append(code)

    return compressed_output, current_bit_limit
```

---

### 4. **Descompressão**

Durante a descompressão, os códigos compactados são traduzidos para suas sequências originais. A lógica considera:

- Se o código já está no dicionário, ele é traduzido diretamente.
- Caso contrário, ele é gerado com base na última sequência decodificada.

```Python
def decompress_with_variable_size(compressed_data, initial_bit_limit, max_bit_limit):
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
            raise ValueError(f"Código inválido: {code}")

        decompressed_output.append(entry)

        if next_code < max_table_size:
            reverse_map[next_code] = current_string + entry[0]
            next_code += 1

            if next_code >= max_table_size and current_bit_limit < max_bit_limit:
                current_bit_limit += 1
                max_table_size = 2 ** current_bit_limit

        current_string = entry

    return "".join(decompressed_output)
```

---

## Conclusão

Este projeto implementa o algoritmo LZW de forma detalhada, combinando eficiência na estrutura de dados (Trie Compacta) e flexibilidade nos tamanhos de código. Ele demonstra a aplicação prática de conceitos avançados de compressão para arquivos de texto e binários.
