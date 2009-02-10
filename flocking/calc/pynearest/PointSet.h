#ifndef _POINTSET_H
#define _POINTSET_H
#include <algorithm>
#include <vector>
#include <cmath>
#include "NeighborList.h"
#include "Tree.h"
template<int d> class MedianFinder;
template<int d>
class PointSet
{
  friend class MedianFinder<d>;
 public:
  typedef double Point[d];
  BoundingBox<d> createBoundingBoxOfSphere(int i, double distance) const;
  void searchTree(int i, const TreeNode<d> * treenode, NeighborList& neighborlist) const;
    
  NeighborList * getNeighborList(int i, int k) const;
  NeighborList * getNeighborListInRealOrder(int i, int k) const;

  Neighbor createNeighbor(int i, int neighbor) const
  {
    return Neighbor(getDistanceSquared(i, neighbor), neighbor);
  }
  const Point& get(int i) const
    {
      return points_[permutation_table_[i]];
    }
  double getSum(int i) const
  {
    double sum = 0;
    for (int a = 0; a < d; a ++)
      sum += get(i)[a];
    return sum;
  }
  double getDistanceSquared(int i, int j) const
  {
    double sum = 0;
    const Point & p1 = get(i), & p2 = get(j);
    for (int a = 0; a < d; a ++)
      sum += (p1[a] - p2[a]) * (p1[a] - p2[a]);
    return sum;
  }
  double getDistance(int i, int j) const
  {
    return std::sqrt(getDistanceSquared(i, j));
  }
  PointSet(Point * points, int N, int m, int r);
  ~PointSet()
    {
      delete root_;
    }
  BoundingBox<d> getBoundingBox();
  TreeNode<d> * createNode(int start, int end, int axis, BoundingBox<d> boundingbox);
  void placeAroundMedians(double median, int start, int end, int axis);
  void init()
  {
    root_ = createNode(0, N_, 0, getBoundingBox());
  }
  void swap(int i, int j)
  {
    std::swap(permutation_table_[i], permutation_table_[j]);
  }
 private:
  Point * points_;
  int N_;
  std::vector<int> permutation_table_;
  TreeNode<d> * root_;
  std::vector<LeafNode<d> *> leaf_;
  int m_;
  int r_;
};

template<int d>
class MedianFinder
{
 public:
  MedianFinder(const PointSet<d> & pointset, int start, int end, int axis, int r);
  double find();
 protected:
  int interval(double x) const
  {
    return std::min(
		    int((x - min_) / (max_ - min_) * r_),
		    r_ - 1);
  }
  double interval_left(int i) const
  {
    return i * (max_ - min_) / r_ + min_;
  }
  double interval_right(int i) const
  {
    return interval_left(i + 1);
  }
  bool x_in_interval(double x, int i) const
  {
    if ((i == 0 && x == min_) || (i == r_ - 1 && x == max_))
      return true;
    return x >= interval_left(i) && x < interval_right(i);
  }
  std::vector<int> count_;
  const PointSet<d> & pointset_;
  int start_, end_, axis_, r_;
  double min_, max_;
};

#include "PointSet.cpp"
#endif
