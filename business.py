from dataclasses import dataclass, asdict, field
import pandas as pd

@dataclass
class Business:
    """Holds business data."""
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None

@dataclass
class BusinessList:
    """Holds list of Business objects and saves to DataFrame."""
    business_list: list[Business] = field(default_factory=list)
    
    def dataframe(self):
        """Transforms business_list to pandas DataFrame."""
        return pd.json_normalize(
            (asdict(business) for business in self.business_list), sep="_"
        )

    def save_to_csv(self, filename):
        """Saves pandas DataFrame to CSV file."""
        self.dataframe().to_csv(f"{filename}.csv", index=False)
