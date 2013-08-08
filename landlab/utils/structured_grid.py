#! /usr/bin/env python


import numpy as np
import itertools


INTERIOR_NODE = 0
FIXED_VALUE_BOUNDARY = 1
FIXED_GRADIENT_BOUNDARY = 2
TRACKS_CELL_BOUNDARY = 3
INACTIVE_BOUNDARY = 4

BAD_INDEX_VALUE = np.iinfo(np.int).max


def node_count(shape):
    """
    The total number of nodes in a structured grid with dimensions given
    by the tuple, *shape*. Where *shape* is the number of node rows and
    node columns.

    >>> node_count((3, 4))
    12
    """
    assert(len(shape) == 2)
    return shape[0] * shape[1]


def cell_count(shape):
    """
    The total number of cells in a structured grid with dimensions, *shape*.
    Where *shape* is a tuple that gives the dimensions of the grid as number
    of rows of nodes followed by number of columns of nodes.

    >>> cell_count((3, 4))
    2
    """
    assert(len(shape) == 2)

    try:
        assert(np.min(shape) > 2)
    except AssertionError:
        return 0
    else:
        return (shape[0] - 2) * (shape[1] - 2)


def active_cell_count(shape):
    """
    Number of active cells. By default, all cells are active so this is
    the same as cell_count.
    """
    return cell_count(shape)


def active_link_count(shape):
    """
    Number of active links in a structured grid with dimensions, *shape*.
    """
    assert(len(shape) == 2)
    return link_count(shape) - 2 * (shape[0] - 1) + 2 * (shape[1] - 1)


def link_count(shape):
    """
    Total (active and inactive) number of links in a structured grid with
    dimensions, *shape*. This is the number of to-links and from-links, not
    the total of the two.

    >>> link_count((3,2))
    7
    """
    assert(len(shape) == 2)
    return shape[1] * (shape[0] - 1) + shape[0] * (shape[1] - 1)


def boundary_cell_count(shape):
    """
    Number of cells that are on the boundary of a structured grid with
    dimensions, *shape*. In fact, cells centered on boundary nodes are not
    really cells. If they were, though, this is how many there would be.

    >>> boundary_cell_count((3, 4))
    10
    """
    assert(len(shape) == 2)
    return 2 * (shape[0] - 2) + 2 * (shape[1] - 2) + 4


def interior_cell_count(shape):
    """
    Number of interior cells. Since cells are only defined on interior nodes,
    this is the same as cell_count.
    """
    return cell_count(shape)


def face_count(shape):
    """
    Total number of faces in a structured grid with dimensions, *shape*. Each
    cell has four faces, and shared faces only count once.

    >>> face_count((3, 4))
    7
    """
    return (shape[0] - 1) * (shape[1] - 2) + (shape[0] - 2) * (shape[1] - 1)


def top_index_iter(shape):
    """
    Iterator for the top boundary indices of a structured grid.
    """
    return xrange(shape[1] * (shape[0] - 1), shape[0] * shape[1])


def bottom_index_iter(shape):
    """
    Iterator for the bottom boundary indices of a structured grid.
    """
    return xrange(0, shape[1])


def left_index_iter(shape):
    """
    Iterator for the left boundary indices of a structured grid.
    """
    return xrange(0, shape[0] * shape[1], shape[1])


def right_index_iter(shape):
    """
    Iterator for the right boundary indices of a structured grid.
    """
    return xrange(shape[1] - 1, shape[0] * shape[1], shape[1])


def left_right_iter(shape, *args):
    """
    Iterator for the left and right boundary indices of a structured grid.
    This iterates over the indices in order rather than iterating all of
    the left boundary and then all of the right boundary.

    >>> import numpy as np
    >>> np.fromiter(left_right_iter((4, 3)), dtype=np.int)
    array([ 0,  2,  3,  5,  6,  8,  9, 11])
    """
    if len(args) == 0:
        iter_rows = xrange(0, shape[0], 1)
    elif len(args) == 1:
        iter_rows = xrange(0, args[0], 1)
    elif len(args) == 2:
        iter_rows = xrange(args[0], args[1], 1)
    elif len(args) == 3:
        iter_rows = xrange(args[0], args[1], args[2])

    for row in iter_rows:
        yield row * shape[1]
        yield row * shape[1] + shape[1] - 1


def bottom_top_iter(shape):
    """
    Iterates of the bottom indices and then the top indices of a structured
    grid.
    """
    return itertools.chain(bottom_index_iter(shape),
                           top_index_iter(shape))


def boundary_iter(shape):
    """
    Iterates over all of the boundary node indices of a structured grid in
    order.
    """
    return itertools.chain(bottom_index_iter(shape),
                           left_right_iter(shape, 1, shape[0] - 1),
                           top_index_iter(shape))


def boundary_nodes(shape):
    """
    An array of the indices of the boundary nodes.

    >>> boundary_nodes((3, 4))
    array([ 0,  1,  2,  3,  4,  7,  8,  9, 10, 11])
    """
    return np.fromiter(boundary_iter(shape), dtype=np.int)


def interior_iter(shape):
    interiors = []
    interiors_per_row = shape[1] - 2
    for row in xrange(shape[1] + 1, shape[1] * (shape[0] - 1), shape[1]):
        interiors.append(xrange(row , row + interiors_per_row))
    return itertools.chain(*interiors)


def interior_nodes(shape):
    return np.fromiter(interior_iter(shape), dtype=np.int)


def node_xyz(shape, *args):
    """
    Get x, y, and z coordinates for nodes in a structured grid with
    dimensions, *shape*.
    """
    assert(len(shape) == 2)

    try:
        spacing = args[0]
    except IndexError:
        spacing = np.ones(len(shape), dtype=np.float)
    else:
        assert(len(spacing) == len(shape))

    try:
        origin = args[1]
    except IndexError:
        origin = np.zeros(len(shape), dtype=np.float)
    else:
        assert(len(origin) == len(origin))

    node_count = np.prod(shape)

    row_y = np.arange(origin[0], shape[0] * spacing[0] + origin[0],
                         spacing[0])
    col_x = np.arange(origin[1], shape[1] * spacing[1] + origin[0],
                         spacing[1])

    (node_x, node_y) = np.meshgrid(col_x, row_y)
    node_z = np.zeros(node_count)

    node_x.shape = (node_count, )
    node_y.shape = (node_count, )

    return (node_x, node_y, node_z)


def active_cells(shape):
    return np.arange(active_cell_count(shape))


def active_cell_node(shape):
    return cell_node_index(shape)


def node_active_cell(shape):
    n_nodes = node_count(shape)

    node_ids = np.arange(n_nodes)
    node_ids.shape = shape

    node_ids[0, :] = BAD_INDEX_VALUE
    node_ids[:, 0] = BAD_INDEX_VALUE
    node_ids[-1, :] = BAD_INDEX_VALUE
    node_ids[:, -1] = BAD_INDEX_VALUE

    node_ids.shape = (n_nodes, )

    return node_ids


def cell_node_index(shape):
    node_ids = np.arange(node_count(shape))
    node_ids.shape = shape

    cell_node = node_ids[1:-1, 1:-1].copy()
    cell_node.shape = ((shape[0] - 2) * (shape[1] - 2), )

    return cell_node


def node_link_index(shape):
    node_ids = np.arange(np.prod(shape))
    node_ids.shape = shape

    return (from_node_links(node_ids), to_node_links(node_ids))


def to_node_links(node_ids):
    vertical_links = node_ids[1:, :]
    horizontal_links = node_ids[:, 1:]
    return np.concatenate((vertical_links.flat, horizontal_links.flat))


def from_node_links(node_ids):
    vertical_links = node_ids[:-1, :]
    horizontal_links = node_ids[:, :-1]
    return np.concatenate((vertical_links.flat, horizontal_links.flat))


def link_faces(shape, actives=None):
    if actives is None:
        actives = active_links(shape)

    num_links = link_count(shape)

    link_faces = np.empty(num_links, dtype=np.int)
    link_faces.fill(BAD_INDEX_VALUE)
    link_faces[actives] = np.arange(len(actives))

    return link_faces


def node_boundary_status(shape):
    status = np.empty(np.prod(shape), dtype=np.int)

    status[interior_nodes(shape)] = INTERIOR_NODE
    status[boundary_nodes(shape)] = FIXED_VALUE_BOUNDARY

    return status


def active_links(shape, node_status=None, link_nodes=None):
    if node_status is None:
        node_status = node_boundary_status(shape)

    if link_nodes is None:
        (link_from_node, link_to_node) = node_link_index(shape)
    else:
        (link_from_node, link_to_node) = link_nodes

    from_node_status = node_status[link_from_node]
    to_node_status = node_status[link_to_node]

    active_links = (((from_node_status == INTERIOR_NODE) & ~
                     (to_node_status == INACTIVE_BOUNDARY)) |
                    ((to_node_status == INTERIOR_NODE) & ~
                     (from_node_status == INACTIVE_BOUNDARY)))

    (active_links, ) = np.where(active_links)

    return active_links


if __name__ == '__main__':
    import doctest
    doctest.testmod()