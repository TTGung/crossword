import copy
import random
from queue import PriorityQueue

class word_bucket:
    def __init__(self, word_list, left, right):
        right = min(right, len(word_list))
        self.word_list = word_list[left:right]
        self.word_list.sort(key=len, reverse=True)
        max_len = len(self.word_list[0])

        self.look_up = [[0 for c in range(27)] for p in range(max_len)]
        for id, word in enumerate(self.word_list):
            for pos, char in enumerate(word):
                self.look_up[pos][word_bucket.get_asc(char)] |= (1 << id)

        self.upper_bound = [0 for l in range(max_len + 1)]
        for id, word in enumerate(self.word_list):
            self.upper_bound[len(word)] |= (1 << id)
        for l in range(1, max_len + 1):
            self.upper_bound[l] |= self.upper_bound[l-1]

    @staticmethod
    def get_asc(char):
        if (char == '*'):
            return 26
        return ord(char) - ord('a')

    def get_upperbound(self, upper):
        if(upper < len(self.upper_bound)):
            return self.upper_bound[upper]
        return self.upper_bound[-1]

    def match(self, pos, char):
        if(pos < len(self.look_up)):
            return self.look_up[pos][word_bucket.get_asc(char)]
        return False

class mutation:
    def __init__(self, row, col, dx, dy, sequence):
        self.row = row
        self.col = col
        self.dx = dx
        self.dy = dy
        self.sequence = sequence

    def predict(self, target):
        return target.word_len + len(self.sequence)

class creature:
    def __init__(self, parent = False, mut = False, choice = False, size = 0, bucket_cnt = 0):
        if(isinstance(parent, creature) == True):
            self.size = parent.size
            self.board = copy.deepcopy(parent.board)
            self.word_len = parent.word_len
            self.mask = copy.deepcopy(parent.mask)
            self.word_choice = parent.word_choice.copy()
            self.mutation_list = copy.deepcopy(parent.mutation_list)
        else:
            self.size = size
            self.board = [['_' for c in range(size)] for r in range(size)]
            self.word_len = 0
            self.mask = [[0 for i in range(size)], [0 for i in range(size)]]
            self.word_choice = [0 for b in range(bucket_cnt)]
            self.mutation_list = []
        self.mutate(mut)
        self.add(choice)

    @staticmethod
    def get_line(row, col, dir):
        return (1 ^ dir) * row + (0 ^ dir) * col, (0 ^ dir) * row + (1 ^ dir) * col

    def mutate(self, mut):
        if (isinstance(mut, mutation) == False):
            return
        dir = (1 & mut.dx) + (0 & mut.dy)
        seq_len = len(mut.sequence)
        line, left = creature.get_line(mut.row, mut.col, dir)
        self.word_len += seq_len
        self.mask[dir][line] |= (1 << (left + seq_len)) - (1 << left)
        self.mask[dir][line] ^= (1 << (seq_len + left - 1)) - (1 << (left + 1))
        self.mutation_list.append(mut)
        for i, c in enumerate(mut.sequence):
            if(self.board[mut.row+(i*mut.dx)][mut.col+(i*mut.dy)] == '_'):
                self.mask[dir^1][left+i] |= (1 << line)
                self.board[mut.row+(i*mut.dx)][mut.col+(i*mut.dy)] = c

    def add(self, choice):
        if (isinstance(choice, tuple) == False):
            return
        bucket_id, word_id = choice
        self.word_choice[bucket_id] |= (1 << word_id)

class genetic_algo:
    def __init__(self, size, word_list, bucket_size, fertility, survivor_cnt, last_gen):
        self.size = size
        self.word_list = ['*'+word+'*' for word in word_list]
        self.bucket_size = bucket_size
        self.bucket = [word_bucket(self.word_list, l, l+bucket_size) for l in range(0, len(self.word_list), bucket_size)]
        self.fertility = min(fertility, 2 * (size**2) * len(self.bucket))
        self.survivor_cnt = survivor_cnt
        self.last_gen = last_gen
        self.fsb = [0 for x in range(1 << 16)]
        for x in range(1 << 16):
            if((x & 1) == 0):
                self.fsb[x] = self.fsb[x >> 1] + 1

    def generate_mutation(self, target, seed):
        invalid = (False, False)
        row, col, dir, bucket_id = seed
        if(target.board[row][col] != '_' and target.board[row][col] != '*'):
            return invalid
        dx, dy = 0 ^ dir, 1 ^ dir
        ptr16, prev, curr = 1, 0, 0
        line, left = creature.get_line(row, col, dir)
        bitmask = (target.mask[dir][line] | (1 << self.size)) >> (left + 1)
        candidate = self.bucket[bucket_id].match(0, '*') ^ target.word_choice[bucket_id]
        pref, flag = False, False
        word_id = 0
        roll_back = target.board[row][col]
        target.board[row][col] = '*'

        while(bitmask > 0):
            nxt16 = bitmask & ((1 << 16) - 1)
            while(nxt16 > 0):
                char = target.board[row+dx*prev][col+dy*prev]
                candidate &= self.bucket[bucket_id].match(prev, char)
                pref |= (char != '_' and char != '*')
                if(candidate == 0):
                    target.board[row][col] = roll_back
                    if(flag == False):
                        return invalid
                    word_id = word_id.bit_length() - 1
                    return (mutation(row, col, dx, dy, self.bucket[bucket_id].word_list[word_id]), (bucket_id, word_id))
                curr = ptr16 + self.fsb[nxt16]
                valid_candidate = candidate & self.bucket[bucket_id].get_upperbound(curr)
                if(valid_candidate != 0):
                    word_id = valid_candidate & (-valid_candidate)
                    flag = pref
                prev = curr
                nxt16 ^= nxt16 & (-nxt16)
            bitmask >>= 16
            ptr16 = ptr16 + 16

        target.board[row][col] = roll_back
        if (flag == False):
            return invalid
        word_id = word_id.bit_length() - 1
        return (mutation(row, col, dx, dy, self.bucket[bucket_id].word_list[word_id]), (bucket_id, word_id))

    def evolve(self):
        not_exist = (False, False, False)
        survivor = [not_exist]
        pq = PriorityQueue()
        parent = [[], []]

        wlen = len(self.word_list)
        samp = random.sample([(id // self.bucket_size, id % self.bucket_size) for id in range(wlen)], min(self.survivor_cnt, wlen))
        parent[0] = [creature(size = self.size, bucket_cnt = len(self.bucket)) for i in range(self.survivor_cnt)]
        for i, (bucket_id, word_id) in enumerate(samp):
            parent[0][i].mutate(mutation(0, 0, 0, 1, '*' * self.size))
            parent[0][i].mutate(mutation(0, 0, 1, 0, '*' * self.size))
            parent[0][i].mutate(mutation(self.size - 1, 0, 0, 1, '*' * self.size))
            parent[0][i].mutate(mutation(0, self.size - 1, 1, 0, '*' * self.size))
            word = self.bucket[bucket_id].word_list[word_id]
            mut = mutation(self.size - 2, self.size - len(word), 0, 1, word)
            pq.put((mut.predict(parent[0][i]), i))
            survivor[i] = (i, False, False)
            survivor.append(not_exist)
            parent[0][i].mutate(mut)
            parent[0][i].add((bucket_id, word_id))
        parity, rem = 0, len(survivor)-1

        seed = tuple((r, c, d, b) for r in range(self.size) for c in range(self.size) for d in range(2) for b in range(len(self.bucket)))
        perm = list(range(len(seed)))

        for g in range(self.last_gen-1):
            random.shuffle(perm)
            for p, curr in enumerate(parent[parity]):
                shift = random.randint(0, len(seed)-1)
                for f in range(self.fertility):
                    (mut, choice) = self.generate_mutation(curr, seed[perm[shift-f]])
                    if(choice == False):
                        continue
                    survivor[rem] = (p, mut, choice)
                    pq.put((mut.predict(curr), rem))
                    if(len(survivor) > self.survivor_cnt):
                        rem = pq.get()[1]
                    else:
                        survivor.append(not_exist)
                        rem += 1
            parent[parity^1] = [creature(parent[parity][p], mut, choice) for i, (p, mut, choice) in enumerate(survivor) if i != rem]
            survivor = [(p, False, False) if(p < rem) else (p-1, False, False) for p in range(len(survivor))]
            parity ^= 1

        return max(parent[parity], key = lambda p: len(p.mutation_list)*10+p.word_len)

class crossword:
    def __init__(self, size, limit, word_list, hint_list, generator = (100, 500, 20)):
        self.size = size+2
        self.limit = limit
        self.match = 0
        self.word_list = []
        self.hint_list = dict()
        for word, hint in zip(word_list, hint_list):
            if(len(word) <= size):
                self.word_list.append(word)
                self.hint_list[word] = hint

        bucket_size, fertility, survivor_cnt = generator
        self.generator = genetic_algo(self.size, self.word_list, bucket_size, fertility, survivor_cnt, limit)
        puzzle = self.generator.evolve()
        self.answer = [['_' if(cell == '*') else cell for cell in row] for row in puzzle.board]
        self.position = [mutation(mut.row+mut.dx, mut.col+mut.dy, mut.dx, mut.dy, mut.sequence[1:-1]) for mut in puzzle.mutation_list if(mut.sequence[1:-1] in self.hint_list)]
        self.board = [['_' for c in range(self.size)] for r in range(self.size)]
        self.remain = self.size**2 - sum([row.count('_') for row in self.answer])

    def update(self, r, c, char):
        prev = (self.board[r][c] == self.answer[r][c])
        self.board[r][c] = char
        curr = (self.board[r][c] == self.answer[r][c])
        self.remain = self.remain - (prev ^ curr) if(curr == True) else self.remain + (prev ^ curr)

    def win(self):
        if(self.remain == 0):
            return True
        return False