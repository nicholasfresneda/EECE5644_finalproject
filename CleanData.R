library (ggplot2)
library(dplyr)
library(lubridate)
options(digits=3)

# Import data
baseData <- read.csv(file="Metro_Interstate_Traffic_Volume.csv", header=TRUE, sep=",", stringsAsFactors = FALSE)

# Remove duplicates and weird outliers
baseData <- unique(baseData)
baseData <- subset(baseData, temp>200 & rain_1h<100 & snow_1h<100)

# Fix and split date_time
baseData$date_time <- paste(baseData$date_time, ":00", sep = "")
baseData$date_time <- as.POSIXct(baseData$date_time, format = "%m/%d/%Y %H:%M:%S")
baseData$hour <- hour(baseData$date_time)
baseData$month <- month(baseData$date_time)
baseData$weekday <- wday(baseData$date_time)
baseData$weekday[baseData$weekday<6] <- 0 # Designates weekday
baseData$weekday[baseData$weekday>5] <- 1 # Designates weekend
baseData$date <- date(baseData$date_time)

# Holidays fix and visual inspection for grouping
# 0 = No holiday
# 1 = High volume travel holiday
# 2 = Low volume travel holiday
hDates <- unique(baseData$date_time[baseData$holiday != "None"])
for (i in 1:length(hDates)) {
  temp <- baseData$holiday[baseData$date_time == hDates[i]]
  baseData$holiday[baseData$date == hDates[i]] <- temp[1]
}
#holidayData <- filter(baseData, holiday != "None")
#ggplot(holidayData, aes(x = traffic_volume, y = holiday)) + geom_point()
baseData$holiday[baseData$holiday == "None"] <- "0"
baseData$holiday[baseData$holiday == "Washingtons Birthday" | baseData$holiday == "Veterans Day" |
                   baseData$holiday == "State Fair" | baseData$holiday == "Columbus Day"] <- "1"
baseData$holiday[baseData$holiday != "0" & baseData$holiday != "1"] <- "2"
#holidayData <- filter(baseData, holiday != "None")
#ggplot(holidayData, aes(x = traffic_volume, y = holiday)) + geom_point()
rm(holidayData, hDates, i, temp)

# Remove variation in capitalization and convert to numeric if necessary
baseData <- mutate_all(baseData, toupper)
baseData$temp  <- as.numeric(baseData$temp)
baseData$rain_1h  <- as.numeric(baseData$rain_1h)
baseData$snow_1h  <- as.numeric(baseData$snow_1h)
baseData$hour  <- as.numeric(baseData$hour)

# Normalize Values
normalizedData <- baseData
normalizedData$temp <- (normalizedData$temp - min(normalizedData$temp)) /
  (max(normalizedData$temp) - min(normalizedData$temp))
normalizedData$rain_1h <- (normalizedData$rain_1h - min(normalizedData$rain_1h)) /
  (max(normalizedData$rain_1h) - min(normalizedData$rain_1h))
normalizedData$snow_1h <- (normalizedData$snow_1h - min(normalizedData$snow_1h)) /
  (max(normalizedData$snow_1h) - min(normalizedData$snow_1h))
normalizedData$hour <- (normalizedData$hour - min(normalizedData$hour)) /
  (max(normalizedData$hour) - min(normalizedData$hour))

# Export to CSV
write.csv(baseData, file = "CleanedData.csv")
write.csv(normalizedData, file = "CleanedNormalizedData.csv")