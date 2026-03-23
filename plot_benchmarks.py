import matplotlib.pyplot as plt
import csv

data = {
    'BruteForce': {'n_rects': [], 'prep_time': [], 'query_time': []},
    'MapBased': {'n_rects': [], 'prep_time': [], 'query_time': []},
    'PersistentTree': {'n_rects': [], 'prep_time': [], 'query_time': []}
}

with open('benchmark_results.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        n_rects = int(row['n_rects'])
        algorithm = row['algorithm']
        prep_time = float(row['prep_time'])
        query_time = float(row['query_time'])
        
        data[algorithm]['n_rects'].append(n_rects)
        data[algorithm]['prep_time'].append(prep_time)
        data[algorithm]['query_time'].append(query_time)

plt.rcParams.update({
    'font.size': 12,
    'figure.figsize': (10, 6),
    'axes.grid': True,
    'grid.alpha': 0.3
})

fig, ax = plt.subplots()
algorithms = ['BruteForce', 'MapBased', 'PersistentTree']
colors = {'BruteForce': 'blue', 'MapBased': 'green', 'PersistentTree': 'red'}
markers = {'BruteForce': 'o', 'MapBased': 's', 'PersistentTree': '^'}

for algo in algorithms:
    ax.plot(data[algo]['n_rects'], data[algo]['prep_time'], 
            marker=markers[algo], color=colors[algo], 
            label=algo, linewidth=2, markersize=8)

ax.set_xlabel('Количество прямоугольников (N)', fontsize=13)
ax.set_ylabel('Время подготовки (сек)', fontsize=13)
ax.set_title('Время подготовки данных', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('preprocessing_time.png', dpi=150, bbox_inches='tight')
print("preprocessing_time.png сохранён")

plt.close()

fig, ax = plt.subplots()

for algo in algorithms:
    ax.plot(data[algo]['n_rects'], data[algo]['query_time'], 
            marker=markers[algo], color=colors[algo], 
            label=algo, linewidth=2, markersize=8)

ax.set_xlabel('Количество прямоугольников (N)', fontsize=13)
ax.set_ylabel('Время запросов (сек)', fontsize=13)
ax.set_title('Время выполнения запросов', fontsize=15, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('query_time.png', dpi=150, bbox_inches='tight')
print("query_time.png сохранён")

plt.close()

print("\nГрафики успешно созданы!")