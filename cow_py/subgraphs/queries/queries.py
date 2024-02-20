from cow_py.subgraphs.client import CoWSubgraphQuery

# /**
#  * GraphQL query for the total number of tokens, orders, traders, settlements, volume, and fees.
#  */
TOTALS_QUERY = """
  query Totals {
    totals {
      tokens
      orders
      traders
      settlements
      volumeUsd
      volumeEth
      feesUsd
      feesEth
    }
  }
"""

# /**
#  * GraphQL query for the total volume over the last N days.
#  * @param days The number of days to query.
#  */
LAST_DAYS_VOLUME_QUERY = """
  query LastDaysVolume($days: Int!) {
    dailyTotals(orderBy: timestamp, orderDirection: desc, first: $days) {
      timestamp
      volumeUsd
    }
  }
"""

# /**
#  * GraphQL query for the total volume over the last N hours.
#  * @param hours The number of hours to query.
#  */
LAST_HOURS_VOLUME_QUERY = """
  query LastHoursVolume($hours: Int!) {
    hourlyTotals(orderBy: timestamp, orderDirection: desc, first: $hours) {
      timestamp
      volumeUsd
    }
  }
"""


class TotalsQuery(CoWSubgraphQuery):
    def get_query(self):
        return TOTALS_QUERY


class LastDaysVolumeQuery(CoWSubgraphQuery):
    def get_query(self):
        return LAST_DAYS_VOLUME_QUERY


class LastHoursVolumeQuery(CoWSubgraphQuery):
    def get_query(self):
        return LAST_HOURS_VOLUME_QUERY
