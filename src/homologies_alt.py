import numpy as np

# FindUnion implementation. Allows to assign data to each union.
class FindUnion:
    def __init__(self):
        self._parent = [0]
        self._rank = [1]
        self._data = [None]

    def add(self):
        num = len(self._parent)
        self._parent += [num]
        self._rank += [1]
        self._data += [None]
        return num

    def union(self, x, y):
        x_par = self.find(x)
        y_par = self.find(y)
        if (x_par == y_par):
            return

        if self._rank[x_par] < self._rank[y_par]:
            self._parent[x_par] = y_par
        elif self._rank[x_par] > self._rank[y_par]:
            self._parent[y_par] = x_par
        else:
            self._parent[y_par] = x_par
            self._rank[x_par] += 1

    def find(self, x):
        x_par = x
        while (self._parent[x_par] != x_par):
            x_par = self._parent[x_par]

        # compress path
        el = x
        while (self._parent[el] != el):
            new_el = self._parent[el]
            self._parent[el] = x_par
            el = new_el

        return x_par

    # We do not know which data to copy, users should set union data manually
    def __getitem__(self, x):
        return self._data[self.find(x)]
    def __setitem__(self, x, val):
        self._data[self.find(x)] = val

    # Capability to iterate over unions' data
    def __iter__(self):
        self._iter_idx = 0
        return self

    def next(self):
        self._iter_idx += 1
        while (self._iter_idx < len(self._parent)
               and self._parent[self._iter_idx] != self._iter_idx):
            self._iter_idx += 1
        if self._iter_idx == len(self._parent):
            raise StopIteration
        return self._data[self._iter_idx]


def get_side_neighbours(image, ix):
    x, y = ix
    maxx, maxy = image.shape
    result = []

    if x > 0:
        result += [(x - 1, y)]
    if y > 0:
        result += [(x, y - 1)]
    if x + 1 < maxx:
        result += [(x + 1, y)]
    if y + 1 < maxy:
        result += [(x, y + 1)]

    return result

def get_corner_neighbours(image, ix):
    x, y = ix
    maxx, maxy = image.shape
    candx = [x - 1, x, x + 1]
    candy = [y - 1, y, y + 1]

    return [(a, b) for a in candx for b in candy
                   if a >= 0 and a < maxx and b >= 0 and b < maxy
                   and not (a == x and b == y)]

# Given image and poset replaces every image value with index of largest
# smaller element in poset, or -1 if there isn't one.
def pixellize(image, poset):
    stack = [(val, ix) for (ix ,val) in np.ndenumerate(image)]
    stack.sort(reverse = True)

    pix = len(poset) - 1    # poset pixellization

    for val, ix in stack:
        while val < poset[pix] and pix >= 0:
            pix -= 1
        image[ix] = pix

# Acts on pixellized data
def _get_homologies(image, nb_fun):
    result = []
    stack = [(val, ix) for (ix ,val) in np.ndenumerate(image)]
    find_union = FindUnion()
    component_nums = np.zeros_like(image, dtype=int)

    # Sort from highest pixel value
    stack.sort(reverse = True)

    for val, ix in stack:
        if val == -1: # These do not belong to the filtrated set
            break

        nonzero_nbs = [nb for nb in nb_fun(image, ix) if component_nums[nb] != 0]
        if not nonzero_nbs: # Isolated component
            new_union = find_union.add()
            component_nums[ix] = new_union
            find_union[new_union] = (val, None) # Start of new hom chain
            continue

        # Assign ix 'some' component
        component_nums[ix] = component_nums[nonzero_nbs[0]]

        # Iterate through consecutive pairs of neighbours
        nb_pairs = zip(nonzero_nbs[1:], nonzero_nbs[:-1])
        for el1, el2 in nb_pairs:
            el1u = find_union.find(component_nums[el1])
            el2u = find_union.find(component_nums[el2])
            if el1u == el2u:
                continue

            # Make a union and end the latter chain (higher component val)
            if el1u > el2u:
                el1u, el2u = el2u, el1u
            older_chain = find_union[el1u]
            newer_chain = find_union[el2u]
            find_union.union(el1u, el2u)
            find_union[el1u] = older_chain

            cs, ce = newer_chain
            result += [(cs, val)]

    # Collect remaining values from still existing components
    result += [(a, -1) for (a, _) in find_union]
    # Throw away all chains that were created and destroyed at the same value
    ret = [(a,b) for (a,b) in result if a != b]
    return ret

def get_zero_homologies(image):
    return _get_homologies(image, get_side_neighbours)

def get_one_homologies(image, n):
    # Use Alexander duality, embedding image onto a sphere.
    # n is the number of filtrations - 1.

    # Add an empty frame around the image to connect outer components
    sx, sy = image.shape
    sx += 2
    sy += 2
    sph_image = np.full((sx, sy), -2, dtype=int)
    sph_image[1:-1, 1:-1] = image

    # Reverse the order of pixels on the image
    sph_image = (-sph_image) + n

    # Now n+2 is the outer frame, n+1 is everything not in the filtrated set,
    # rest are reverse filtrations of the set
    result = _get_homologies(sph_image, get_corner_neighbours)
    # remove the outer (reduced) homology to match Alexander duality
    tmp = [(a,b) for a, b in result if a != n + 2]
    # finally inverse the chains - we're guarateed there are no '(_, -1)'
    # chains except for the one removed above
    result = [(n - b, n - a) for a, b in tmp]
    return result

def get_homologies(image, n):
    return (get_zero_homologies(image), get_one_homologies(image, n))
