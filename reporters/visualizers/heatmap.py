import os
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional
from core.types import AnalysisResult
from core.i18n import t
import config

def generate_heatmap(result: AnalysisResult, output_dir: str) -> Optional[str]:
    heatmap_data = getattr(result, 'heatmap_data', None)
    if not heatmap_data:
        return None

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            days = [t('mon'), t('tue'), t('wed'), t('thu'), t('fri'), t('sat'), t('sun')]
            hours = list(range(24))
            
            matrix = np.zeros((7, 24))
            for (weekday, hour), count in heatmap_data.items():
                if 0 <= weekday < 7 and 0 <= hour < 24:
                    matrix[weekday, hour] = count

            df = pd.DataFrame(matrix, index=days, columns=hours)

            plt.figure(figsize=(16, 8))
            sns.heatmap(df, cmap="YlGnBu", linewidths=.5, cbar=True)
            
            plt.title(t('heatmap-title'))
            plt.xlabel(t('heatmap-x'))
            plt.ylabel(t('heatmap-y'))
            
            filename = os.path.join(output_dir, 'heatmap.png')
            plt.tight_layout()
            plt.savefig(filename, dpi=200)
            plt.close()
            
        return None
    except Exception as e:
        return f"Heatmap Error: {str(e)}"