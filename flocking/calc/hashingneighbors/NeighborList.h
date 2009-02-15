#ifndef _NEIGHBORLIST_H
#define _NEIGHBORLIST_H
#include <utility>
#include <algorithm>
#include <vector>
#include <iostream>
#include <stdexcept>
/**
   A pair representing a distance squared to the original point and the
   index of the neighbor.
*/
typedef std::pair<double, int> Neighbor;
/**
   List of neighbors of a point, sorted in nearest to farthest.

   Is represented as a heap of Neighbor objects.

   Use the iterators begin() and end() to iterate the neighbors list.
*/
class NeighborList
{
 protected:
  // Neighbors, arranged as a heap. These are not sorted
  typedef std::vector<Neighbor> List;
 public:
  typedef List::const_iterator const_iterator;
 public:
  /** Return an iterator pointing to the beginning of the list */
  List::const_iterator begin() const
  {
    return list_.begin();
  }
  /** Return an iterator pointing to the end of the list */
  List::const_iterator end() const
  {
    return list_.end();
  }
  /** Return the first element (farthest one) */
  List::const_reference farthest() const
  {
    return list_.front();
  }

 public:
  /** Construct a NeighborList of desired_size neighbors */
  NeighborList(int desired_size) : desired_size_(desired_size)
  {
    list_.reserve(desired_size + 1);
  }

  /** Return the list size */
  int size() const
  {
    return list_.size();
  }
  /** Check if the list has the requested size */
  bool hasDesiredSize() const
  {
    return size() == desired_size_;
  }
  double getFarthestNeighborDistance(double default_value)
  {
    if (!hasDesiredSize())
      return default_value;
    return farthest().first;
  }
  void addNeighbor(const Neighbor& neighbor)
  {
    list_.push_back(neighbor);
    std::push_heap(list_.begin(), list_.end());
  }
  void removeFarthestNeighbor()
  {
    if (list_.empty())
      throw std::out_of_range("List is empty");
    std::pop_heap(list_.begin(), list_.end());
    list_.pop_back();
  }
  /** Add a Neighbor in the list, and remove the farthest element if
      necessary */
  void addNeighborAndTrim(const Neighbor& neigbhor)
  {
    addNeighbor(neigbhor);
    trim();
  }
  /** Trim the list if it is too big */
  void trim()
  {
    while (size() > desired_size_)
      removeFarthestNeighbor();
  }
  void sortFinalResults()
  {
    std::sort_heap(list_.begin(), list_.end());
  }
  /** Change the order of the list from internal order to real order,
      using the permutation_table given from PointSet */
  void changeToRealOrder(const std::vector<int> & permutation_table)
  {
    List::iterator it;
    for (it = list_.begin(); it != list_.end(); ++it)
      it->second = permutation_table[it->second];
  }
  /** Clear the list */
  void clear()
  {
    list_.clear();
  }

 protected:
  List list_;
  int desired_size_;
};

#endif
