#include <algorithm>
#include <exception>
#include <list>
#include <cmath>
#include <utility>
template<int d> class PointSet;
template<int d>
class BoundingBox
{
 public:
  typedef std::pair<double, double> Interval;

  friend class PointSet<d>;
  std::pair<BoundingBox<d>, BoundingBox<d> >
    splitAroundPoint(double median, int axis) 
    {
    BoundingBox<d> first(*this), second(*this);
    first.interval_[axis].second = median;
    second.interval_[axis].first = median;
    return std::pair<BoundingBox<d>, BoundingBox<d> >(first, second);
  }
  bool intersect(const BoundingBox & other)
  {
    for (int a = 0; a != d; ++a)
      if (!intervalIntersect(interval_[a], other.interval_[a]))
	return false;
    return true;
  }
 protected:
  bool intervalIntersect(Interval a, Interval b)
  {
    return (a.first <= b.first && b.first <= a.second) ||
      (b.first <= a.first && a.first <= b.second);
  }
  std::pair<double, double> interval_[d];
};

template<int d>
class TreeNode
{
 public:
 TreeNode(int start, int end, BoundingBox<d> boundingbox) :
  start_(start), end_(end), boundingbox_(boundingbox) { }
  virtual ~TreeNode() { }
  const BoundingBox<d> & getBoundingBox() const
  {
    return boundingbox_;
  }
 protected:
  BoundingBox<d> boundingbox_;
  int start_;
  int end_;
};

template<int d>
class BranchNode : public TreeNode<d>
{
 public:
  BranchNode(int start, int end, BoundingBox<d> boundingbox,
	     int axis, double median,
	     TreeNode<d> * left, TreeNode<d> * right) :
  TreeNode<d>(start, end, boundingbox), axis_(axis), median_(median),
    left_(left), right_(right) { }
  virtual ~BranchNode()
    {
      delete left_;
      delete right_;
    }
  const TreeNode<d> * getLeftChild() const
  {
    return left_;
  }
  const TreeNode<d> * getRightChild() const
  {
    return right_;
  }
 protected:
  TreeNode<d> * left_, * right_;
  int axis_;
  double median_;
};
template<int d> class HashTable;

template<int d>
class LeafNode : public TreeNode<d>
{
 public:
 LeafNode(int start, int end, BoundingBox<d> boundingbox,
	  HashTable<d> * hashtable) :
  TreeNode<d>(start, end, boundingbox), hashtable_(hashtable) { }
  virtual ~LeafNode()
    {
      delete hashtable_;
    }
  const HashTable<d> * getHashTable() const
  {
    return hashtable_;
  }
 protected:
  HashTable<d> * hashtable_;
};

