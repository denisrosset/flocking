#include "HashTable.h"

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
PointSet<d>::createBoundingBoxOfSphere(int i, double distance) const
{
  BoundingBox<d> boundingbox;
  for (int a = 0; a != d; ++a) {
    boundingbox.interval_[a].first = get(i)[a] - distance;
    boundingbox.interval_[a].second = get(i)[a] + distance;
  }
  return boundingbox;
}

template<int d>
void 
PointSet<d>::searchTree(int i, const TreeNode<d> * treenode,
			NeighborList& neighborlist) const
{
  BoundingBox<d> current_boundingbox = 
    createBoundingBoxOfSphere(i, std::sqrt(neighborlist.back().first));
  if (!current_boundingbox.intersect(treenode->getBoundingBox()))
    return;
  const LeafNode<d> * leafnode = dynamic_cast<const LeafNode<d> *>(treenode);
  if (leafnode) {
    if (leafnode->getHashTable() != leaf_[i]->getHashTable())
      leafnode->getHashTable()->refineNearestNeighbors(i, neighborlist);
  }
  else {
    const BranchNode<d> * branchnode = dynamic_cast<const BranchNode<d> *>(treenode);
    searchTree(i, branchnode->getLeftChild(), neighborlist);
    searchTree(i, branchnode->getRightChild(), neighborlist);
  }
}

template<int d>
NeighborList * 
PointSet<d>::getNeighborList(int i, int k) const
{
  if (k >= m_)
    throw std::out_of_range("Too many neighbors requested for what is precalculated");
  if (!root_)
    throw std::logic_error("Call init() before using getNeighborList");
  int index = std::find(permutation_table_.begin(), permutation_table_.end(), i) - permutation_table_.begin();
  NeighborList * neighborlist = new NeighborList(k);
  leaf_[index]->getHashTable()->getTableNeighbors(index, *neighborlist);
  leaf_[index]->getHashTable()->refineNearestNeighbors(index, *neighborlist, true);
  searchTree(index, root_, *neighborlist);
  return neighborlist;
}

template<int d>
NeighborList *
PointSet<d>::getNeighborListInRealOrder(int i, int k) const
{
  NeighborList * neighborlist = getNeighborList(i, k);
  neighborlist->changeToRealOrder(permutation_table_);
  return neighborlist;
}
template<int d>
PointSet<d>::PointSet(Point * points, int N, int m, int r) :
  points_(points), N_(N), m_(m), r_(r), root_(NULL)
{
  permutation_table_.resize(N);
  leaf_.resize(N);
  for(int i = 0; i < N_; i ++)
    permutation_table_[i] = i;
}
