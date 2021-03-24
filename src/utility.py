
import random

#####################################################################

inf = float('inf')


class ImpossibleError(RuntimeError):
    pass

#####################################################################

def random_permutation(n, m):
    ## [0, n) の範囲から互いに異なる m 個の整数をランダムに選出する
    permutation = []
    for i in range(m):
        permutation.append(random.randint(0, n - i))
    for i in range(m):
        for j in range(i + 1, m):
            if permutation[i] <= permutation[j]:
                permutation[j] += 1
    return permutation


def random_permutations(n, m, c):
    ## n 個の対象から互いに異なる m 個を選ぶ方法をランダムに c 通り選出する
    ## random_permutations(10, 2, 3) => [[8, 3], [2, 5], [1, 9]]
    ## 各組み合わせでは同じ数字が繰り返し出現しないし, 同じ組み合わせも繰り返し出現しない
    permutations = random_permutation(fact(n) // fact(n - m), c)
    for i, p in enumerate(permutations):
        pp = []
        for j in range(m):
            pp.append(p % (n - j))
            p //= n - j
        for j in range(m):
            for k in range(j + 1, m):
                if pp[j] <= pp[k]:
                    pp[k] += 1
        permutations[i] = pp
    return permutations

#####################################################################

class Graph:
    ## 重みなし有向グラフ

    def __init__(self, n):
        self._n   = n
        self._adj = [set() for _ in range(n)]


    def add_edge(self, u, v):
        self._adj[u].add(v)


    def next_to(self, v):
        return self._adj[v]


    def is_connected(self, u, v):
        return v in self.next_to(u)


    def vertices(self):
        return range(self.size())


    def edges(self):
        return [(u, v) for u in self.vertices() for v in self.next_to(u)]


    def size(self):
        return self._n


    @classmethod
    def make_random(cls, n, p):
        ## ランダムなグラフを生成する
        ## n: 頂点数, p: u -> v の辺が生成される確率
        ## 辺数はだいたい n * p
        self = cls(n)
        for u in range(n):
            for v in range(n):
                if u != v and random.random() < p:
                    self.add_edge(u, v)
        return self


    @classmethod
    def make_random_fix(cls, n, e):
        ## 頂点数 n, 辺数 e のグラフをランダムに生成する
        self = cls(n)
        for u, v in random_permutations(n, 2, e):
            self.add_edge(u, v)
        return self


    @classmethod
    def make_barabasi(cls, n, m):
        ## albert barabasi モデルに従ってグラフを生成する
        ## 生成されるグラフはスケールフリー性, スモールワールド性, クラスター性, べき乗則を満たす (はず)
        ## n: 頂点数, m: 大きくすると辺の数が増える
        ## 辺数は m * (m - 1) / 2 + m * (n - m) = m * (2 * n - m - 1) / 2
        ## 生成されるグラフは連結ではないかもしれないし, 重辺を含むかもしれない
        ## 無向グラフしか生成できない
        self = cls(n)
        for u in range(m):
            for v in range(m):
                self.add_edge(u, v)
        for u in range(m + 1, n):
            for _ in range(m):
                v = wchoice((v, len(graph.next_to(v))) for v in range(u))
                self.add_edge(u, v)
                self.add_edge(v, u)
        return self


    def show(self):
        ## require graphviz
        ## try `apt install graphviz && pip install graphviz`
        import graphviz
        dot = graphviz.Digraph()
        for v in self.vertices():
            dot.node(str(v))
        for u in self.vertices():
            for v in self.next_to(u):
                dot.edge(str(u), str(v))
        dot.view()


    def distance(self, u, v):
        q = collections.deque([u])
        memo = { u : 0 }
        while q:
            w = q.popleft()
            if w == v:
                return memo[w]
            for x in self.next_to(w):
                if x in memo:
                    continue
                memo[x] = memo[w] + 1
                q.append(x)
        return inf

#####################################################################

class callviabracket:
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def __getitem__(self, *args, **kwargs):
        return self._wrapped(*args, **kwargs)

#####################################################################
