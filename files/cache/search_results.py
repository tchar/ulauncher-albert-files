from time import time

class SearchResults:
    KEEP_MAX = 4
    KEEP_FOR = 0

    def __init__(self):
        self._results = _SearchResults()
        self._entries = _SearchResults()

    def get_results(self, query):
        return self._results.get(query, exact=True)

    def get_entries(self, query):
        return self._entries.get(query)

    def add_results(self, query, results):
        self._results.add(query, results)

    def add_entries(self, query, entries):
        self._entries.add(query, entries)

    def clear(self):
        self._results.clear()
        self._entries.clear()

class _SearchResults:
    def __init__(self):
        self._terms = []
        self._data = {}
        self._times = {}

    def _time_or_get(self, key):
        if time() - self._times[key] > SearchResults.KEEP_FOR:
            del self._data[key]
            del self._times[key]
            self._terms.remove(key)
        else:
            self._times[key] = time()
            return self._data[key]

    def get(self, query, exact=False):
        if query in self._data:
            return self._time_or_get(query)
        
        if exact: return

        search_terms = sorted(self._terms, key=len, reverse=True)
        for term in search_terms:
            if query.startswith(term):
                result = self._time_or_get(term)
                if result: return result

    def add(self, query, items):
        if SearchResults.KEEP_FOR == 0:
            self.clear()
            return
        self._terms.append(query)
        self._data[query] = items
        self._times[query] = time()

        while len(self._terms) > SearchResults.KEEP_MAX:
            entry = self._terms.pop(0)
            del self._data[entry]
            del self._times[entry]
        
    def clear(self):
        self._terms = []
        self._data = {}
        self._times = {}