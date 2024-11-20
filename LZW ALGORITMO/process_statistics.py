import json
import matplotlib.pyplot as plt

def load_statistics(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def plot_statistics(stats):
    plt.figure(figsize=(14, 7))

    plt.subplot(1, 2, 1)
    plt.plot(stats['compressed_output'], label='Saída Comprimida')
    plt.xlabel('Passos')
    plt.ylabel('Tamanho da Saída Comprimida')
    plt.title('Tamanho da Saída Comprimida ao Longo do Tempo')
    plt.legend()

    max_steps = len(stats['compressed_output'])
    max_value = max(stats['compressed_output'])
    max_axis = max(max_steps, max_value)
    plt.axis([0, max_axis, 0, max_axis])

    plt.subplot(1, 2, 2)
    plt.plot(stats['trie_size'], label='Tamanho da Trie')
    plt.xlabel('Passos')
    plt.ylabel('Tamanho da Trie')
    plt.title('Tamanho da Trie ao Longo do Tempo')
    plt.legend()

    plt.tight_layout()
    plt.savefig('compression_statistics.png')
    plt.show()

def generate_report(stats):
    print("Relatório de Estatísticas de Compressão/Descompressão")
    print("="*50)
    print(f"Tempo de Compressão: {stats['compression_time']:.4f} segundos")
    print(f"Tamanho Original: {stats['original_size']} bytes")
    print(f"Tamanho Comprimido: {stats['compressed_size']} bytes")
    print(f"Taxa de Compressão: {stats['compressed_size'] / stats['original_size']:.4f}")
    print(f"Tempo de Descompressão: {stats['decompression_time']:.4f} segundos")

    plot_statistics(stats)

if __name__ == "__main__":
    stats = load_statistics('stats.json')
    generate_report(stats)