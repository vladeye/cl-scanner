gig_sql = "INSERT INTO gigs (dategig, linkgig) " \
          "SELECT '" + datetime + "', '" + linkgig + "' " \
                                                     "WHERE NOT EXISTS(SELECT 1 FROM gigs WHERE dategig = '" + datetime + "' AND linkgig = '" + linkgig + "')"