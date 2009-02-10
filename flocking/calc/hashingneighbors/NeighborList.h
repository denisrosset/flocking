#ifndef _NEIGHBORLIST_H
#define _NEIGHBORLIST_H
#include <utility>
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

   Is represented as a list of Neighbor objects.

   Use the iterators begin() and end() to iterate the neighbors list.
*/
class NeighborList
{
 protected:
  // for ~ 8 elements, vector is faster than list !
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
  /** Return the first element (closer one) */
  List::const_reference front() const
  {
    return list_.front();
  }
  /** Return the last element (farthest one) */
  List::const_reference back() const
  {
    return list_.back();
  }

 public:
  /** Construct a NeighborList of desired_size neighbors */
  NeighborList(int desired_size) : size_(0), desired_size_(desired_size) { }

  /** Return the list size */
  int size() const
  {
    return size_;
  }
  /** Check if the list has the requested size */
  bool hasDesiredSize() const
  {
    return size_ == desired_size_;
  }
  void addNeighbor(const Neighbor& neighbor)
  {
    List::iterator place;
    if (!size_)
      place = list_.begin();
    else
      place = std::upper_bound(list_.begin(), list_.end(), neighbor);
    list_.insert(place, neighbor);
    size_ ++;
  }
  void removeFarthestNeighbor()
  {
    if (list_.empty())
      throw std::out_of_range("List is empty");
    list_.pop_back();
    size_ --;
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
    while (size_ > desired_size_)
      removeFarthestNeighbor();
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
    size_ = 0;
    list_.clear();
  }

 protected:
  List list_;
  int size_;
  int desired_size_;
};

#endif
