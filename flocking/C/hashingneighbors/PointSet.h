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
   
   All operations in this library except get(Wrap)NeighborListInRealOrder
   return indices that refer to the reordered set of points.

   \param d Dimensionality of space.
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
  PointSet(const Point * points, int N, int m, int r);
  /** Prepare the data structure for efficient queries. Must be called
      once before any query. */
  void init();
  /** Return a NeighborList representing the k-nearest neighbors of
      the point i.
      
      All indices returned by this function are in 'real
      order', that is the order of the point array passed to the PointSet
      constructor.
      
      \param pt the point whose neighbors are queried
      \param k number of neighbors (must be <= m)
      \return The NeighborList queried (must be freed by caller)
  */
  NeighborList * getNeighborListInRealOrder(const Point& pt, int k) const;
  /** Return a NeighborList representing the k-nearest neighbors of
      the point i.

      Assume a torus geometry of size L x L.
      
      All indices returned by this function are in 'real order', that
      is the order of the point array passed to the PointSet
      constructor.

      \param pt the point whose neighbors are queried
      \param k number of neighbors (must be <= m)
      \return The NeighborList queried (must be freed by caller)
  */
  NeighborList * getWrapNeighborListInRealOrder(const Point& pt, int k,
						double L) const;

 public:
  // The following methos are of internal use

  /** Returns a NeighborList representing the k-nearest neighbors of
      the point i.
      
      All indices returned by this function are in
      'internal order', that is the order of elements after
      reorganization around medians.

      \param pt the point whose neighbors are queried
      \param k number of neighbors (must be <= m)
      \return The NeighborList queried (must be freed by caller)
  */
  NeighborList * getNeighborList(const Point& pt, int k) const;

  /** Return a BoundingBox bounding a sphere centered on Point i,
      radius distance.
      
      \param i index of center of sphere, internal order
      \param distance radius of the sphere
  */
  BoundingBox<d> createBoundingBoxOfSphere(const Point& pt, double distance) const;

  /** Refines a NeighborList around i by searching the subtree TreeNode

      \param pt Point to search the nearest neighbors of
      \param projected_pt Nearest point to pt inside bounding box of PointSet
      \param treenode TreeNode to explore
      \param neighbor Current NeighborList to refine
      \param distance_squared_upper_bound In case the NeighborList is not full, upper bound on the kth neighbor distance
  */
  void searchTree(const Point& pt, const Point& projected_pt,
		  const TreeNode<d> * treenode,
		  NeighborList& neighborlist,
		  double distance_squared_upper_bound) const;
    
  /** Create a Neighbor object to be part of a NeighborList */
  Neighbor createNeighbor(const Point& pt, int neighbor) const
  {
    return Neighbor(getDistanceSquared(pt, get(neighbor)), neighbor);
  }

  /** Get a point
      
      \param i the point to get, internal order
  */
  const Point& get(int i) const
    {
      return points_[permutation_table_[i]];
    }
  /** Get the sum of coordinates of a point

      \param pt the point whose sum to calculate
  */
  static double getSum(const Point& pt)
  {
    double sum = 0;
    for (int a = 0; a < d; a ++)
      sum += pt[a];
    return sum;
  }
  static void copyPoint(Point& destination, const Point& source)
  {
    for (int a = 0; a < d; a ++)
      destination[a] = source[a];
  }
  /** Get the distance squared between two points

      \param p1 first point
      \param p2 second point
  */
  double getDistanceSquared(const Point& p1, const Point& p2) const
  {
    double sum = 0;
    for (int a = 0; a < d; a ++)
      sum += (p1[a] - p2[a]) * (p1[a] - p2[a]);
    return sum;
  }
  /** Get the distance between two points

      \param p1 first point
      \param p2 second point
  */
  double getDistance(const Point& p1, const Point& p2) const
  {
    return std::sqrt(getDistanceSquared(p1, p2));
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

  /** Get the leaf containing the point pt inside tree treenode */
  const LeafNode<d> * getLeafFromPoint(const Point& pt,
				       const TreeNode<d> * treenode) const;

  /** Get the leaf containing the point pt, or nearest to it */
  const LeafNode<d> * getLeafNearestFromPoint(const Point& pt) const;


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
  const Point * points_;
  int N_;
  int m_;
  int r_;
  std::vector<int> permutation_table_;
  TreeNode<d> * root_;
  std::vector<LeafNode<d> *> leaf_;
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
