import time
import csv
import bisect
from typing import List, Tuple


class BruteForceSolver:
    def __init__(self, rectangles: List[Tuple[int, int, int, int]]):
        self.rectangles = rectangles
    
    def prepare(self):
        pass
    
    def query(self, x: int, y: int) -> int:
        count = 0
        for x1, y1, x2, y2 in self.rectangles:
            if x1 <= x < x2 and y1 <= y < y2:
                count += 1
        return count


class MapBasedSolver:
    def __init__(self, rectangles: List[Tuple[int, int, int, int]]):
        self.rectangles = rectangles
        self.x_coords = []
        self.y_coords = []
        self.grid = None
    
    def prepare(self):
        if not self.rectangles:
            self.x_coords = []
            self.y_coords = []
            self.grid = []
            return
        
        x_set = set()
        y_set = set()
        for x1, y1, x2, y2 in self.rectangles:
            x_set.add(x1)
            x_set.add(x2)
            y_set.add(y1)
            y_set.add(y2)
        
        self.x_coords = sorted(x_set)
        self.y_coords = sorted(y_set)
        
        x_map = {x: i for i, x in enumerate(self.x_coords)}
        y_map = {y: i for i, y in enumerate(self.y_coords)}
        
        nx = len(self.x_coords)
        ny = len(self.y_coords)
        
        diff = [[0] * (ny + 1) for _ in range(nx + 1)]
        
        for x1, y1, x2, y2 in self.rectangles:
            x1_idx = x_map[x1]
            y1_idx = y_map[y1]
            x2_idx = x_map[x2]
            y2_idx = y_map[y2]
            
            diff[x1_idx][y1_idx] += 1
            diff[x2_idx][y1_idx] -= 1
            diff[x1_idx][y2_idx] -= 1
            diff[x2_idx][y2_idx] += 1
        
        self.grid = [[0] * (ny + 1) for _ in range(nx + 1)]
        for i in range(nx):
            for j in range(ny):
                self.grid[i + 1][j + 1] = (
                    self.grid[i][j + 1] + 
                    self.grid[i + 1][j] - 
                    self.grid[i][j] + 
                    diff[i][j]
                )
    
    def query(self, x: int, y: int) -> int:
        if self.grid is None:
            self.prepare()
        
        if not self.x_coords or not self.y_coords:
            return 0
        
        x_idx = bisect.bisect_right(self.x_coords, x) - 1
        y_idx = bisect.bisect_right(self.y_coords, y) - 1
        
        if x_idx < 0 or y_idx < 0:
            return 0
        
        return self.grid[x_idx + 1][y_idx + 1]


class PersistentNode:
    __slots__ = ('left', 'right', 'value')
    
    def __init__(self, left=None, right=None, value=0):
        self.left = left
        self.right = right
        self.value = value


class PersistentSegmentTree:
    def __init__(self, y_coords: List[int]):
        self.y_coords = sorted(set(y_coords))
        self.size = len(self.y_coords)
    
    def build(self, l: int, r: int) -> PersistentNode:
        if l > r:
            return None
        if l == r:
            return PersistentNode(value=0)
        mid = (l + r) // 2
        left_child = self.build(l, mid)
        right_child = self.build(mid + 1, r)
        return PersistentNode(left_child, right_child, 0)
    
    def update(self, node: PersistentNode, l: int, r: int, ql: int, qr: int, delta: int) -> PersistentNode:
        if ql > qr or l > r:
            return node
        
        if node is None:
            node = self.build(l, r)
            if node is None:
                return None
        
        if ql <= l and r <= qr:
            return PersistentNode(node.left, node.right, node.value + delta)
        
        mid = (l + r) // 2
        left_child = node.left
        right_child = node.right
        
        if ql <= mid and left_child is not None:
            left_child = self.update(left_child, l, mid, ql, min(qr, mid), delta)
        if qr > mid and right_child is not None:
            right_child = self.update(right_child, mid + 1, r, max(ql, mid + 1), qr, delta)
        
        return PersistentNode(left_child, right_child, node.value)
    
    def query(self, node: PersistentNode, l: int, r: int, pos: int) -> int:
        if node is None or l > r or l > pos or r < pos:
            return 0
        
        res = node.value
        
        if l == r:
            return res
        
        mid = (l + r) // 2
        if pos <= mid:
            res += self.query(node.left, l, mid, pos)
        else:
            res += self.query(node.right, mid + 1, r, pos)
        
        return res


class PersistentTreeSolver:
    def __init__(self, rectangles: List[Tuple[int, int, int, int]]):
        self.rectangles = rectangles
        self.x_coords = []
        self.version_map = {}
        self.tree = None
        self.empty = False
    
    def prepare(self):
        if not self.rectangles:
            self.empty = True
            self.x_coords = []
            self.version_map = {}
            return
        
        y_set = set()
        events = []
        
        for x1, y1, x2, y2 in self.rectangles:
            events.append((x1, 1, y1, y2))
            events.append((x2, -1, y1, y2))
            y_set.add(y1)
            y_set.add(y2)
        
        if not y_set:
            self.empty = True
            return
        
        events.sort(key=lambda e: e[0])
        
        self.tree = PersistentSegmentTree(list(y_set))
        
        if self.tree.size < 2:
            self.empty = True
            return
        
        root = self.tree.build(0, self.tree.size - 2)
        
        i = 0
        n = len(events)
        
        first_x = events[0][0]
        self.x_coords.append(first_x - 1)
        self.version_map[first_x - 1] = root
        
        while i < n:
            current_x = events[i][0]
            
            j = i
            while j < n and events[j][0] == current_x:
                _, delta, y1, y2 = events[j]
                
                y1_idx = bisect.bisect_left(self.tree.y_coords, y1)
                y2_idx = bisect.bisect_left(self.tree.y_coords, y2) - 1
                
                if 0 <= y1_idx <= y2_idx < self.tree.size - 1:
                    root = self.tree.update(root, 0, self.tree.size - 2, y1_idx, y2_idx, delta)
                
                j += 1
            
            self.x_coords.append(current_x)
            self.version_map[current_x] = root
            
            i = j
        
        self.x_coords.sort()
    
    def query(self, x: int, y: int) -> int:
        if not self.version_map and not self.empty:
            self.prepare()
        
        if self.empty:
            return 0
        
        idx = bisect.bisect_right(self.x_coords, x) - 1
        if idx < 0:
            return 0
        
        x_key = self.x_coords[idx]
        root = self.version_map.get(x_key)
        if root is None:
            return 0
        
        y_idx = bisect.bisect_right(self.tree.y_coords, y) - 1
        
        if y_idx < 0 or y_idx >= self.tree.size - 1:
            return 0
        
        return self.tree.query(root, 0, self.tree.size - 2, y_idx)


def generate_rectangles(n: int) -> List[Tuple[int, int, int, int]]:
    rectangles = []
    for i in range(n):
        x1 = 10 * i
        y1 = 10 * i
        x2 = 10 * (2 * n - i)
        y2 = 10 * (2 * n - i)
        rectangles.append((x1, y1, x2, y2))
    return rectangles

def generate_queries(n_rects: int, n_queries: int) -> List[Tuple[int, int]]:
    queries = []
    p1 = 1000000007
    p2 = 1000000009
    max_coord = 20 * n_rects
    
    for i in range(n_queries):
        x = pow(p1 * i, 31, max_coord)
        y = pow(p2 * i, 31, max_coord)
        queries.append((x, y))
    
    return queries

def run_benchmarks():
    configs = [
        (100, 1000),
        (500, 5000),
        (1000, 10000),
        (2000, 20000),
        (3000, 30000),
        (4000, 40000),
        (5000, 50000),
        (10000, 100000)
    ]
    
    results = []
    
    for n_rects, n_queries in configs:
        print(f"\nЗапуск бенчмарка: N={n_rects}, Q={n_queries}")
        rectangles = generate_rectangles(n_rects)
        queries = generate_queries(n_rects, n_queries)
        
        bf = BruteForceSolver(rectangles)
        t0 = time.perf_counter()
        bf.prepare()
        t1 = time.perf_counter()
        for x, y in queries:
            bf.query(x, y)
        t2 = time.perf_counter()
        results.append({
            'n_rects': n_rects,
            'n_queries': n_queries,
            'algorithm': 'BruteForce',
            'prep_time': t1 - t0,
            'query_time': t2 - t1,
            'total_time': t2 - t0
        })
        print(f"  BruteForce: prep={t1-t0:.4f}s, query={t2-t1:.4f}s")
        
        if n_rects <= 4000:
            mb = MapBasedSolver(rectangles)
            t0 = time.perf_counter()
            mb.prepare()
            t1 = time.perf_counter()
            for x, y in queries:
                mb.query(x, y)
            t2 = time.perf_counter()
            results.append({
                'n_rects': n_rects,
                'n_queries': n_queries,
                'algorithm': 'MapBased',
                'prep_time': t1 - t0,
                'query_time': t2 - t1,
                'total_time': t2 - t0
            })
            print(f"  MapBased:   prep={t1-t0:.4f}s, query={t2-t1:.4f}s")
        else:
            print("  MapBased:   пропущен (слишком долго для такого N)")
        
        pt = PersistentTreeSolver(rectangles)
        t0 = time.perf_counter()
        pt.prepare()
        t1 = time.perf_counter()
        for x, y in queries:
            pt.query(x, y)
        t2 = time.perf_counter()
        results.append({
            'n_rects': n_rects,
            'n_queries': n_queries,
            'algorithm': 'PersistentTree',
            'prep_time': t1 - t0,
            'query_time': t2 - t1,
            'total_time': t2 - t0
        })
        print(f"  PersistentTree: prep={t1-t0:.4f}s, query={t2-t1:.4f}s")
        
        with open('benchmark_results.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['n_rects', 'n_queries', 'algorithm', 'prep_time', 'query_time', 'total_time'])
            writer.writeheader()
            writer.writerows(results)
    
    print("\nБенчмарки завершены. Результаты в benchmark_results.csv")

if __name__ == "__main__":
    run_benchmarks()