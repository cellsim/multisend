#include <assert.h>
#include <stdio.h>
#include <iostream>

#include "processforecaster.hh"

// each component corresponding to one rate marked by midpoint
std::vector< Process > ProcessForecastTick::make_components( const Process & example )
{
  std::vector< Process > components;

  example.pmf().for_each( [&] ( const double midpoint, const double & value, unsigned int index )
			  {
			    Process component( example );
			    component.set_certain( midpoint );
			    assert( components.size() == index );
			    assert( example.pmf().index( midpoint ) == index );
			    components.push_back( component );
			  } );
  return components;
}

ProcessForecastTick::ProcessForecastTick( const double tick_time,
					  const Process & example,
					  const unsigned int upper_limit )
  : _count_probability()
{
  /* step 1: make the component processes */
  std::vector< Process > components( make_components( example ) );

  /* step 2: for each process component, find the distribution of arrivals */
  for ( auto it = components.begin(); it != components.end(); it++ ) {
    // probablity for each packet count in a given packet rate
    std::vector< double > this_count_probability;
    double total = 0.0;
    for ( unsigned int i = 0; i < upper_limit; i++ ) {
      // probability when count i packets get through when the average rate is the one in the component
      const double prob = it->count_probability( tick_time, i );
      this_count_probability.push_back( prob );
      total += prob;
#if DEBUG
      std::cout << "component " << std::distance(components.begin(), it) << ", count for " << i << ", prob = " << prob << ", total = " << total << std::endl;
      // std::cin.get();
#endif
    }
    assert( total < 1.0 + (1e-10) );
    this_count_probability.push_back( 1.0 - total );

    // std::copy(this_count_probability.begin(), this_count_probability.end(), std::ostream_iterator<double>(std::cout, " "));

    /* append to cache */
    // for each rate, we have the probablity for different packet count can sent in interval
    // now we have a two dimension table to look up probability, given rate and paceket count
    _count_probability.push_back( this_count_probability );
    // std::cin.get();
  }
}

double ProcessForecastTick::probability( const Process & ensemble, unsigned int count ) const
{
  assert( ensemble.is_normalized() );
  assert( ensemble.pmf().size() == _count_probability.size() );
  assert( _count_probability.size() > 0 );

  assert( count < _count_probability[ 0 ].size() );

  double ret = 0.0;

  ensemble.pmf().for_each( [&] ( const double midpoint, const double & value, unsigned int index )
			   {
			     ret += value * _count_probability[ index ][ count ];
          //  std::cout << "["<< index << "]" << "count for " << count << ", value = " << value
          //   << " prob = " << _count_probability[ index ][ count ] << " ret = " << ret << std::endl;
			   } );

  assert( ret <= 1.0 );

#if DEBUG
  std::cout << "probablity for count " << count << ": " << ret << std::endl;
#endif
  return ret;
}

std::vector< double > ProcessForecastInterval::convolve( const std::vector< double > & old_count_probabilities,
							 const std::vector< double > & this_tick )
{
  std::vector< double > ret( old_count_probabilities.size() + this_tick.size() - 1 );

  for ( unsigned int old_count = 0; old_count < old_count_probabilities.size(); old_count++ ) {
    for ( unsigned int new_count = 0; new_count < this_tick.size(); new_count++ ) {
      ret[ old_count + new_count ] += old_count_probabilities[ old_count ] * this_tick[ new_count ];
    }
  }

  return ret;
}

ProcessForecastInterval::ProcessForecastInterval( const double tick_time,
						  const Process & example,
						  const unsigned int tick_upper_limit,
						  const unsigned int num_ticks )
  : _count_probability()
{
  /* step 1: make the component processes */
  std::vector< Process > components( ProcessForecastTick::make_components( example ) );

  // for (const auto& comp: components) {
  //   comp.pmf().for_each( [&] ( const double midpoint, const double & value, unsigned int index )
	// 		  {
	// 		     std::cout << "[" << index << "]" << "midpoint = " << midpoint << ", value = " << value << std::endl;
	// 		  } 
  //   );
  // }
 
  /* step 2: make the tick forecast */
  ProcessForecastTick tick_forecast( tick_time, example, tick_upper_limit );

  /* step 3: for each component, integrate and evolve forward */
  // for each rate, get the probability of packet count can sent in next num_ticks, this is fixed and won't be changed
  // and will be used to combine with real time observations
  for ( auto it = components.begin(); it != components.end(); it++ ) {
    std::vector< double > this_component_count_probability( 1, 1.0 );
    for ( unsigned int tick = 0; tick < num_ticks; tick++ ) {
      /* collect tick forecast */
      std::vector< double > this_tick;
      // found bug here, should add =, otherwise the sum of this_component_count_probability won't be equal to 1
      for ( unsigned int i = 0; i <= tick_upper_limit; i++ ) {
	        it->normalize();
          this_tick.push_back( tick_forecast.probability( *it, i ) );
          // std::cout << "normalize component " << std::distance(components.begin(), it) << ": \n" << *it << std::endl;
          //std::cin.get();
      }

      // std::copy(this_tick.begin(), this_tick.end(), std::ostream_iterator<double>(std::cout, " "));
      // std::cout << "\ntick forcast " << tick << ", component " << std::distance(components.begin(), it) << ": ";

      /* add to previous forecast */
      // std::copy(this_component_count_probability.begin(), this_component_count_probability.end(), std::ostream_iterator<double>(std::cout, " "));
      // std::cout << "\nthis_component_count_probability size: " << this_component_count_probability.size() << std::endl;
      
      this_component_count_probability = convolve( this_component_count_probability,
						   this_tick );

      /* evolve forward */
      it->evolve( tick_time );
      // std::cout << "component " << std::distance(components.begin(), it) << ": \n" << *it << std::endl;
      // std::cin.get();
    }

#if DEBUG
    std::cout << "[" << std::distance(components.begin(), it) << "] this_component_count_probability size: " << this_component_count_probability.size() << ", ";
    std::copy(this_component_count_probability.begin(), this_component_count_probability.end(), std::ostream_iterator<double>(std::cout, " "));
    std::cout << std::endl;
#endif

    // debugging for issue when sum is not equal to 1
    // double sum = 0.0;
    // for (auto it = this_component_count_probability.begin(); it != this_component_count_probability.end(); ++it) {
    //   sum += *it;
    // }
    // std::cout << "sum[" << std::distance(components.begin(), it) << "] = " << sum << std::endl;
    // std::cin.get();

    _count_probability.push_back( this_component_count_probability );
  }
}

/* exact same routine as for ProcessForecastTick! */
double ProcessForecastInterval::probability( const Process & ensemble, unsigned int count ) const
{
  assert( ensemble.is_normalized() );
  assert( ensemble.pmf().size() == _count_probability.size() );
  assert( _count_probability.size() > 0 );

  assert( count < _count_probability[ 0 ].size() );

  double ret = 0.0;

  ensemble.pmf().for_each( [&] ( const double midpoint, const double & value, unsigned int index )
			   {
			     ret += value * _count_probability[ index ][ count ];
			   } );

  assert( ret <= 1.0 );

  return ret;
}

void ProcessForecastInterval::printProbability( const Process & ensemble) const
{
  double sum = 0.0;
  for ( unsigned int i = 0; i < _count_probability[ 0 ].size(); i++ ) {
    double prob = probability( ensemble, i );
    sum += prob;
    std::cout << "predict for count " << i << ", prob = " << prob << ", percentile = " << sum << std::endl;
  }
}

unsigned int ProcessForecastInterval::lower_quantile( const Process & ensemble, const double x ) const
{
  double sum = 0.0;

  for ( unsigned int i = 0; i < _count_probability[ 0 ].size(); i++ ) {
    sum += probability( ensemble, i );

    if ( sum >= x ) {
      return i;
    }
  }

  return _count_probability[ 0 ].size() + 1;
}
