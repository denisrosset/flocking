template<int d>
HashTable<d>::HashTable(const PointSet<d> & pointset, int start, int end)
  : pointset_(pointset), start_(start), end_(end)
{
  size_ = end - start;
  table_.resize(size_);
  maxsum_ = minsum_ = PointSet<d>::getSum(pointset_.get(start));
  for (int i = start + 1; i < end; i ++) {
    double coordsum = PointSet<d>::getSum(pointset_.get(i));
    minsum_ = std::min(minsum_, coordsum);
    maxsum_ = std::max(maxsum_, coordsum);
  }
  key_ = (size_ - 1) / (maxsum_ - minsum_);
  for (int i = start; i < end; i ++) {
    int index = getIndex(pointset_.get(i));
    table_[index].push_back(i);
  }
}

template<int d>
void
HashTable<d>::processDistanceFromBucket(const Point& pt, int bucket,
					int& number, double& max_distance_sq,
					int k) const
{
  PointList::const_iterator it;
  for (it = table_[bucket].begin(); it != table_[bucket].end(); ++it) {
    if (number == k)
      return;
    double distance = pointset_.getDistanceSquared(pt, pointset_.get(*it));
    max_distance_sq = std::max
      (max_distance_sq, distance);
    number ++;
  }
}

template<int d>
double
HashTable<d>::getKthNeighborDistanceSquaredUpperBound(const Point& pt, int k) const
{
  int number = 0;
  double max_distance_sq = 0;
  int bucket = getIndex(pt);
  processDistanceFromBucket(pt, bucket, number, max_distance_sq, k);
  for (int j = 1; j < size_; j ++) {
    if (number == k)
      return max_distance_sq;
    if(bucket + j < size_)
      processDistanceFromBucket(pt, bucket + j, number, max_distance_sq, k);
    if(bucket - j >= 0)
      processDistanceFromBucket(pt, bucket - j, number, max_distance_sq, k);
  }
  throw std::runtime_error("Could not process enough neighbors");
}

template<int d>
void
HashTable<d>::refineNearestNeighbors(const Point& pt, 
				     NeighborList & neighborlist,
				     double distance_squared_upper_bound) const
{
  double dsquared = neighborlist.hasDesiredSize() ? neighborlist.back().first 
                                        : distance_squared_upper_bound;
  double sumpt = PointSet<d>::getSum(pt);
  double dimfact = std::sqrt(d * dsquared);
  int start = int(
		  (sumpt - minsum_ - dimfact) * key_);
  int end = int(std::ceil(
			  (sumpt - minsum_ + dimfact) * key_)) + 1;
  start = std::max(start, 0);
  end = std::min(end, size_);
  for (int j = start; j < end; j++) {
    PointList::const_iterator it;
    for (it = table_[j].begin(); it != table_[j].end(); ++it) {
      double distance_squared =
	pointset_.getDistanceSquared(pt, pointset_.get(*it));
      double distance_bound = neighborlist.hasDesiredSize() ?
	neighborlist.back().first : distance_squared_upper_bound;
      if (distance_squared <= distance_bound)
	neighborlist.addNeighborAndTrim(pointset_.createNeighbor(pt, *it));
    }
  }
  if (neighborlist.size() == 0)
    throw std::logic_error("Should not be empty");
}
