#include <vector>
#include <stdio.h>
#include <iostream>
#include <assert.h>

#include "process.hh"
#include "processforecaster.hh"

using namespace std;

int main(void)
{
  std::cout.setf(std::ios::fixed, std::ios::floatfield);
  std::cout.setf(std::ios::showpoint);

  Process myprocess(2000, 300, 5, 64);
// ProcessForecastTick tick_forecast( 0.02, myprocess, 30);
  ProcessForecastInterval forecastr(0.02, myprocess, 30, 1);

  std::cout << myprocess;
  for (int i=0; i<10; ++i) {
    myprocess.evolve(0.02);
    if (i<5) {
      myprocess.observe(0.02, 0.02 * 1000);
    } else {
      myprocess.observe(0.02, 0.02 * 500);
    }
    myprocess.normalize();
    std::cout << "round [" << i << "]\n" << myprocess;
    forecastr.printProbability(myprocess);
    std::cout << "predict: " << forecastr.lower_quantile(myprocess, 0.05) << std::endl;
  }

  // std::vector< Process > components( ProcessForecastTick::make_components( myprocess ) );
  // for ( auto it = components.begin(); it != components.end(); it++ ) {
  //   if (std::distance(components.begin(), it) == 5) {
  //     for (int i=0; i<5; ++i) {
  //       it->evolve( 0.02 );
  //       it->normalize();
  //       std::cout << "round [" << i << "]\n" << *it;
  //     }
  //   }
  // }



  // myprocess.normalize();

  // const int predict_ticks = 10;
  // const int interval_ms = 10;

  // ProcessForecastInterval forecastr((double)interval_ms / 1000.0, myprocess, 30, predict_ticks);

  // int current_chunk = -1, count = -1;

  // int predicted_counts = 0;
  // int predict_end = 0;
  // int actual_counts = 0;

  // fprintf(stderr, "Ready...\n");

  // int worse_than_predicted = 0, total_predictions = 0;

  // while (cin.good())
  // {
  //   int ms = 0;
  //   cin >> ms;

  //   if (current_chunk == -1)
  //   { /* need to initialize */
  //     current_chunk = ms / interval_ms;
  //     count = 0;
  //   }

  //   if (ms == 0 && current_chunk != 0)
  //   {
  //     break;
  //   }

  //   assert(ms / interval_ms >= current_chunk);

  //   while (current_chunk < ms / interval_ms)
  //   {
  //     myprocess.evolve((double)interval_ms / 1000.0);
  //     myprocess.observe((double)interval_ms / 1000.0, count);
  //     myprocess.normalize();

  //     if (current_chunk >= predict_end)
  //     {
  //       total_predictions++;

  //       if (actual_counts < predicted_counts - 1)
  //       {
  //         worse_than_predicted++;
  //       }

  //       printf("%d actual = %d predicted = %d diff = %d\n",
  //              ms, actual_counts, predicted_counts, actual_counts - predicted_counts);

  //       predict_end = current_chunk + predict_ticks;
  //       actual_counts = 0;
  //       predicted_counts = forecastr.lower_quantile(myprocess, 0.15);
  //     }

  //     current_chunk++;
  //     count = 0;
  //   }

  //   count++;
  //   actual_counts++;
  // }

  // fprintf(stderr, "Results: %d/%d (= %f %%) were worse than predicted.\n",
  //         worse_than_predicted,
  //         total_predictions,
  //         100.0 * (double)worse_than_predicted / (double)total_predictions);
}
