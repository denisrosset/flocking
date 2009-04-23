#include "HashTable.h"
#include <cmath>

template<int d>
void PointSet<d>::init()
{
  root_ = createNode(0, N_, 0, getBoundingBox());
}

template<int d>
MedianFinder<d>::MedianFinder(const PointSet<d> & pointset, int start, int end, int axis, int r) :
  pointset_(pointset), start_(start), end_(end), axis_(axis), r_(r)
{
  min_ = pointset.get(0)[axis];
  max_ = pointset.get(0)[axis];
  for (int i = 0; i != pointset.N_; ++ i) {
    double x = pointset_.get(i)[axis];
    min_ = std::min(min_, x);
    max_ = std::max(max_, x);
  }
  count_.resize(r_);
}

template<int d>
double
MedianFinder<d>::find()
{
  for (int i = start_; i != end_; ++i)
    count_[interval(pointset_.get(i)[axis_])] ++;
  int median_index = (end_ - start_) / 2;
  int total = 0;
  int histo_i = -1;
  for (int i = 0; i != r_; ++i) {
    if (total + count_[i] > median_index) {
      histo_i = i;
      break;
    }
    total += count_[i];
  }
  std::vector<double> points;
  for(int i = start_; i != end_; ++i) {
    double x = pointset_.get(i)[axis_];
    if (x_in_interval(x, histo_i))
      points.push_back(x);
  }
  sort(points.begin(), points.end());
  double median = points[median_index - total];
  return median;
}

template<int d>
TreeNode<d> *
PointSet<d>::createNode(int start, int end, int axis, BoundingBox<d> boundingbox)
{
  if (end - start > 2 * m_) {
    double median = MedianFinder<d>(*this, start, end, axis, r_).find();
    placeAroundMedians(median, start, end, axis);
    int median_i = (start + end) / 2;
    std::pair<BoundingBox<d>, BoundingBox<d> > 
      child_bboxes = boundingbox.splitAroundPoint(median, axis);
    int next_axis = (axis + 1) % d;
    TreeNode<d> * left = 
      createNode(start, median_i, next_axis, child_bboxes.first);
    TreeNode<d> * right = 
      createNode(median_i, end, next_axis, child_bboxes.second);
    return new BranchNode<d>(start, end, boundingbox, axis, median, left, right);
  } else {
    HashTable<d> * hashtable = new HashTable<d>(*this, start, end);
    LeafNode<d> * leaf = new LeafNode<d>(start, end, boundingbox, hashtable);
    for (int i = start; i != end; ++i)
      leaf_[i] = leaf;
    return leaf;
  }
}
template<int d>
BoundingBox<d>
PointSet<d>::getBoundingBox()
{
  BoundingBox<d> bbox;
  for (int a = 0; a < d; ++ a)
    bbox.interval_[a].first = bbox.interval_[a].second = get(0)[a];
  for (int i = 0; i < N_; ++ i) {
    for (int a = 0; a < d; ++ a) {
      bbox.interval_[a].first = std::min(bbox.interval_[a].first, get(i)[a]);
      bbox.interval_[a].second = std::max(bbox.interval_[a].second, get(i)[a]);
    }
  }
  return bbox;
}

template<int d>
void
PointSet<d>::placeAroundMedians(double median, int start, int end, int axis)
{
  int left = 0, middle = 0, right = 0;
  for (int i = start; i != end; ++i) {
    double x = get(i)[axis];
    if (x < median) left ++;
    if (x == median) middle ++;
    if (x > median) right ++;
  }
  int median_i = start + left;
  for (int i = start; i != end; ++i) {
    if (i >= start + left && i < start + left + middle)
      continue;
    double x = get(i)[axis];
    if (x == median) {
      while (get(median_i)[axis] == median)
	median_i ++;
      swap(i, median_i);
    }
  }
  int left_i = start;
  int right_i = start + left + middle;
  while (left_i < start + left) {
    if (get(left_i)[axis] > median) {
      while (get(right_i)[axis] > median)
	right_i ++;
      swap(left_i, right_i);
    }
    left_i ++;
  }
}

template<int d>
BoundingBox<d>
PointSet<d>::createBoundingBoxOfSphere(const Point& pt, double distance) const
{
  BoundingBox<d> boundingbox;
  for (int a = 0; a != d; ++a) {
    boundingbox.interval_[a].first = pt[a] - distance;
    boundingbox.interval_[a].second = pt[a] + distance;
  }
  return boundingbox;
}

template<int d>
void 
PointSet<d>::searchTree(const Point& pt,
			const Point& projected_pt,
			const TreeNode<d> * treenode,
			NeighborList& neighborlist,
			double distance_squared_upper_bound) const
{
  double distance_squared = neighborlist.getFarthestNeighborDistance
    (distance_squared_upper_bound);
  BoundingBox<d> current_boundingbox = 
    createBoundingBoxOfSphere(pt, std::sqrt(distance_squared));
  if (!current_boundingbox.intersect(treenode->getBoundingBox()))
      return;
  if (treenode->isLeafNode()) {
    const LeafNode<d> * leafnode = static_cast<const LeafNode<d> *>(treenode);
    leafnode->getHashTable()
      ->refineNearestNeighbors(pt, neighborlist, distance_squared_upper_bound);
  } else {
    const BranchNode<d> * branchnode =
      static_cast<const BranchNode<d> *>(treenode);
    if (branchnode->getLeftChild()->getBoundingBox().contains(projected_pt)) {
      searchTree(pt, projected_pt, branchnode->getLeftChild(),
		 neighborlist, distance_squared_upper_bound);
      searchTree(pt, projected_pt, branchnode->getRightChild(),
		 neighborlist, distance_squared_upper_bound);
    } else {
      searchTree(pt, projected_pt, branchnode->getRightChild(),
		 neighborlist, distance_squared_upper_bound);
      searchTree(pt, projected_pt, branchnode->getLeftChild(),
		 neighborlist, distance_squared_upper_bound);
    }
  }
}

template<int d>
NeighborList * 
PointSet<d>::getNeighborList(const Point& pt, int k) const
{
  if (k > m_)
    throw std::out_of_range("Too many neighbors requested for what is precalculated");
  if (!root_)
    throw std::logic_error("Call init() before using getNeighborList");
  NeighborList * neighborlist = new NeighborList(k);
  double distance_squared_upper_bound = getLeafNearestFromPoint(pt)
    ->getHashTable()->getKthNeighborDistanceSquaredUpperBound(pt, k);
  Point projected_pt;
  copyPoint(projected_pt, pt);
  root_->getBoundingBox().forceInside(projected_pt);
  searchTree(pt, projected_pt, root_, *neighborlist, distance_squared_upper_bound);
  return neighborlist;
}

template<int d>
NeighborList *
PointSet<d>::getNeighborListInRealOrder(const Point& pt, int k) const
{
  NeighborList * neighborlist = getNeighborList(pt, k);
  neighborlist->changeToRealOrder(permutation_table_);
  return neighborlist;
}


template<int d>
NeighborList *
PointSet<d>::getWrapNeighborListInRealOrder(const Point& pt, int k,
					    double L) const
{
  NeighborList * neighborlist = getNeighborList(pt, k);
  double distance = std::sqrt(neighborlist->getFarthestNeighborDistance(L/2));
  if (distance == L)
    throw std::logic_error("Bad distance");
  int direction_of_wrap[d], number_of_wraps = 0;
  for (int a = 0; a < d; a ++) {
    direction_of_wrap[a] = 0;
    if (pt[a] - distance < 0 || pt[a] + distance > L) {
      number_of_wraps ++;
      if ((L - pt[a]) < pt[a])
	direction_of_wrap[a] = 1;
      else
	direction_of_wrap[a] = -1;
    }
  }
  int number_of_cases = (1 << number_of_wraps);
  for (int ccase = 1; ccase < number_of_cases; ccase ++) {
    Point candidate;
    copyPoint(candidate, pt);
    int pattern = ccase;
    for (int a = 0; a < d; a ++) {
      if (direction_of_wrap[a]) {
	if (pattern % 2)
	  candidate[a] -= L * direction_of_wrap[a];
	pattern >>= 1;
      }
    }
    Point projected_pt;
    copyPoint(projected_pt, candidate);
    root_->getBoundingBox().forceInside(projected_pt);
    searchTree(candidate, projected_pt, root_, *neighborlist, 0);
  }
  neighborlist->changeToRealOrder(permutation_table_);
  return neighborlist;
}

template<int d>
PointSet<d>::PointSet(const Point * points, int N, int m, int r) :
  points_(points), N_(N), m_(m), r_(r), root_(NULL)
{
  permutation_table_.resize(N_);
  leaf_.resize(N_);
  for(int i = 0; i < N_; i ++)
    permutation_table_[i] = i;
}

template<int d>
const LeafNode<d> *
PointSet<d>::getLeafFromPoint(const Point& pt,
			      const TreeNode<d> * treenode = NULL) const
{
  if (!treenode)
    treenode = root_;
  const LeafNode<d> * leafnode = dynamic_cast<const LeafNode<d> *>(treenode);
  if (leafnode)
    return leafnode;
  else {
    const BranchNode<d> * branchnode = 
      dynamic_cast<const BranchNode<d> *>(treenode);
    if (branchnode->getLeftChild()->getBoundingBox().contains(pt))
      return getLeafFromPoint(pt, branchnode->getLeftChild());
    if (branchnode->getRightChild()->getBoundingBox().contains(pt))
      return getLeafFromPoint(pt, branchnode->getRightChild());
    throw std::runtime_error("Problem with bounding boxes");
  }
}

template<int d>
const LeafNode<d> *
PointSet<d>::getLeafNearestFromPoint(const Point& pt) const
{
  Point nice;
  for (int a = 0; a < d; a ++)
    nice[a] = pt[a];
  root_->getBoundingBox().forceInside(nice);
  return getLeafFromPoint(nice, root_);
}
