from .base import BaseAnalyzer

class GroupAnalyzer(BaseAnalyzer):
    def finalize(self):
                                                     
        super().finalize()
        
        total_msgs = self.result.global_stats.total_messages
        if total_msgs == 0:
            return

                                                  
        sorted_users = sorted(
            self.result.users_stats.items(),
            key=lambda x: x[1].total_messages,
            reverse=True
        )
        
        cumulative_msgs = 0
        core_count = 0
        cutoff = 0.8 * total_msgs
        
        for _, stats in sorted_users:
            cumulative_msgs += stats.total_messages
            core_count += 1
            if cumulative_msgs >= cutoff:
                break
        
        self.result.active_core_count = core_count
        total_users = len(self.result.users_stats)
        if total_users > 0:
            self.result.active_core_pct = (core_count / total_users) * 100