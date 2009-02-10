#ifndef _POINTSET_H
#define _POINTSET_H
#include <algorithm>
#include <vector>
#include <cmath>
#include "NeighborList.h"
#include "Tree.h"
template<int d> class MedianFinder;
template<int d>
/**
   An implementation of the k-nearest neighbor computation algorithm
   described in (BibTex format) :
   
   @inproceedings{793036,
   Address = {Washington, DC, USA},
   Author = {M. Vanco and G. Brunnett and Th. Schreiber},
   Booktitle = {CGI '99: Proceedings of the International Conference on Computer Graphics},
   Pages = {120},
   Publisher = {IEEE Computer Society},
   Title = {A Hashing Strategy for Efficient k -Nearest Neighbors Computation},
   Year = {1999}}
   
   PointSet is non-destructive, it works on an array of points without
   copying or modifying anything. It reorders elements internally using a
   permutation table.
   
   All operations in this library except getNeighborListInRealOrder
   return indices that refer to the reordered set of points.
*/

class PointSet
{
  friend class MedianFinder<d>;
 public:
  typedef double Point[d];
 public:
  // The following methods are to be called externally

  /** Construct a PointSet object.

      \param points an array of points of type double[N][d]
      \param N number of points in the array
      \param m upper bound of the number of neighbors queried
      \param r number of intervals used when seeking the median
  */
  PointSet(Point * points, int N, int m, int r);
  /** Prepare the data structure for efficient queries. Must be called
      once before any query. */
  void init();
  /** Returns a NeighborList representing the k-nearest neighbors of
      the point i.
      
      All indices passed and returned by this function are in 'real
      order', that is the order of the point array passed to the PointSet
      constructor.
      
      \param i the point whose neighbors are queried
      \param k number of neighbors (must be < m)
      \return The NeighborList queried (must be freed by caller)
  */
  NeighborList * getNeighborListInRealOrder(int i, int k) const;

 public:
  // The following methos are of internal use

  /** Returns a NeighborList representing the k-nearest neighbors of
      the point i.
      
      All indices passed and returned by this function are in
      'internal order', that is the order of elements after
      reorganization around medians.

      \param i the point whose neighbors are queried
      \param k number of neighbors (must be < m)
      \return The NeighborList queried (must be freed by caller)
  */
  NeighborList * getNeighborList(int i, int k) const;

  /** Return a BoundingBox bounding a sphere centered on Point i,
      radius distance.
      
      \param i index of center of sphere, internal order
      \param distance radius of the sphere
  */
  BoundingBox<d> createBoundingBoxOfSphere(int i, double distance) const;

  /** Refines a NeighborList around i by searching the subtree TreeNode */
  void searchTree(int i, const TreeNode<d> * treenode, NeighborList& neighborlist) const;
    
  /** Create a Neighbor object to be part of a NeighborList */
  Neighbor createNeighbor(int i, int neighbor) const
  {
    return Neighbor(getDistanceSquared(i, neighbor), neighbor);
  }

  /** Get a point
      
      \param i the point to get, internal order
  */
  const Point& get(int i) const
    {
      return points_[permutation_table_[i]];
    }
  /** Get the sum of coordinates of a point

      \param i the point whose sum to calculate, internal order
  */
  double getSum(int i) const
  {
    double sum = 0;
    for (int a = 0; a < d; a ++)
      sum += get(i)[a];
    return sum;
  }
  /** Get the distance squared between two points

      \param i first point, internal order
      \param j second point, internal order
  */
  double getDistanceSquared(int i, int j) const
  {
    double sum = 0;
    const Point & p1 = get(i), & p2 = get(j);
    for (int a = 0; a < d; a ++)
      sum += (p1[a] - p2[a]) * (p1[a] - p2[a]);
    return sum;
  }
  /** Get the distance between two points

      \param i first point, internal order
      \param j second point, internal order
  */
  double getDistance(int i, int j) const
  {
    return std::sqrt(getDistanceSquared(i, j));
  }

  /* Destructor. Delete the whole tree. Other objects are cleanup
     automatically. */
  ~PointSet()
    {
      delete root_;
    }
  /** Get the box bounding all the points in the PointSet */
  BoundingBox<d> getBoundingBox();
 protected:
  /** Create a node in the tree.
      
      \param start Start element in the PointSet, internal order
      \param end End element in the PointSet, internal order
      \param axis Axis around which to do the median cut
      \param boundingbox BoundingBox of the points between [start,
      end)
      
      \return A TreeNode, either a branch, either a leaf (with hashtable)
  */
  TreeNode<d> * createNode(int start, int end, int axis, BoundingBox<d> boundingbox);
  /** Do a partial sort of the elements in [start, end) around the
  axis specified.

  Put in order :
  - all the elements where the coordinate 'axis' is less than 'median'
  - all the elements where the coordinate 'axis' is equal to the
  'median'
  - all the elements where the coordinate 'axis' is greater than
  'median'
  \param median Value of the median element
  \param start Start element in the PointSet, internal order
  \param end End element in the PointSet, internal order
  \param axis Axis to use in the partial sort
  */
  void placeAroundMedians(double median, int start, int end, int axis);
  /** Swap two elements in the PointSet. No modification is done to
  the original point array, because of the usage of a permutation
  table.
  \param i First element to swap, internal order
  \param j Second element to swap, internal order
  */
  void swap(int i, int j)
  {
    std::swap(permutation_table_[i], permutation_table_[j]);
  }

 protected:
  Point * points_;
  int N_;
  std::vector<int> permutation_table_;
  TreeNode<d> * root_;
  std::vector<LeafNode<d> *> leaf_;
  int m_;
  int r_;
};

/** Class dedicated to find the median of a subset of a PointSet in
    O(N) time. Uses O(r) memory. */
template<int d>
class MedianFinder
{
 public:

  /** Construct the MedianFinder on interval [start, end) of a PointSet.

      \param pointset PointSet on which to do the computation
      \param start Starting point in the PointSet, internal order
      \param end Ending point in the PointSet, internal order
      \param axis Axis to use
      \param r Number of interval in the histogram
  */
  MedianFinder(const PointSet<d> & pointset, int start, int end, int axis, int r);
  /** Compute the median.
      \return The median.
  */
  double find();
 protected:
  /** Return the index of the interval comprising x */
  int interval(double x) const
  {
    return std::min(
		    int((x - min_) / (max_ - min_) * r_),
		    r_ - 1);
  }
  /** Return the left border of the ith interval */
  double interval_left(int i) const
  {
    return i * (max_ - min_) / r_ + min_;
  }
  /** Return the right border of the ith interval */
  double interval_right(int i) const
  {
    return interval_left(i + 1);
  }
  /** Tests if x is in the ith interval */
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
