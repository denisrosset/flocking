#include <algorithm>
#include <exception>
#include <list>
#include <cmath>
#include <utility>
template<int d> class PointSet;
/** Represent a (hyper)rectangular bounding box in d dimensions */
template<int d>
class BoundingBox
{
 public:
  typedef std::pair<double, double> Interval;
 public:
  /** Split the box around a coordinate in a specified axis */
  friend class PointSet<d>;
  std::pair<BoundingBox<d>, BoundingBox<d> >
    splitAroundPoint(double median, int axis) 
    {
    BoundingBox<d> first(*this), second(*this);
    first.interval_[axis].second = median;
    second.interval_[axis].first = median;
    return std::pair<BoundingBox<d>, BoundingBox<d> >(first, second);
  }
  /** Check if the BoundingBox is intersecting with another BoundingBox */
  bool intersect(const BoundingBox & other)
  {
    for (int a = 0; a != d; ++a)
      if (!intervalIntersect(interval_[a], other.interval_[a]))
	return false;
    return true;
  }
 protected:
  /** Check if two Intervals are intersecting */
  bool intervalIntersect(Interval a, Interval b)
  {
    return (a.first <= b.first && b.first <= a.second) ||
      (b.first <= a.first && a.first <= b.second);
  }
  std::pair<double, double> interval_[d];
};

/** Represent a node in the binary tree.

    A node can be either a leaf or a branch.

    Never meant to be instantiated directly.
*/
template<int d>
class TreeNode
{
 public:
  /** Never called directly
      \param start Starting point in the PointSet
      \param end Ending point in the PointSet
      \param boundingbox BoundingBox of the subset of points
  */
 TreeNode(int start, int end, BoundingBox<d> boundingbox) :
  start_(start), end_(end), boundingbox_(boundingbox) { }
  virtual ~TreeNode() { }
  /** Get the BoundingBox of branch */
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
  /** Instantiate a branch in the tree

      \param start Starting point in the PointSet
      \param end Ending point in the PointSet
      \param boundingbox BoundingBox of the subset of points
      \param axis Axis around which the cut is made
      \param median Median on which the cut is made
      \param left Left child
      \param right Right child
  */
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

/** Leaf node, owning an HashTable

    Will delete the HashTable on destruction
*/
template<int d>
class LeafNode : public TreeNode<d>
{
 public:
  /** Instantiate a leaf in the tree
      
      \param start Starting point in the PointSet
      \param end Ending point in the PointSet
      \param boundingbox BoundingBox of the subset of points
      \param hashtable HashTable for the subset of points, will be owned
  */

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

