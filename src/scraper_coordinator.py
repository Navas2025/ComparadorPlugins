"""
Coordinator for managing multiple scraper instances with independent lifecycle.
"""
import queue
import time
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, Future


class TaskState(Enum):
    """States for scraping tasks."""
    PENDING = "pending"
    ACTIVE = "active"
    FINISHED = "finished"
    FAILED = "failed"


@dataclass
class ScraperTask:
    """Represents a single scraping operation."""
    identifier: str
    scraper_type: Any
    state: TaskState = TaskState.PENDING
    result_data: Dict = field(default_factory=dict)
    item_count: int = 0
    completed_at: Optional[str] = None
    error_info: Optional[str] = None
    page_limit: int = 5


class ScraperCoordinator:
    """Manages concurrent scraping operations with state tracking."""
    
    def __init__(self, worker_pool_size=4):
        self._task_registry = {}
        self._executor = ThreadPoolExecutor(max_workers=worker_pool_size)
        self._futures = {}
        
    def register_task(self, task_id: str, scraper_cls, pages: int = 5):
        """Register a new scraping task."""
        task = ScraperTask(
            identifier=task_id,
            scraper_type=scraper_cls,
            page_limit=pages
        )
        self._task_registry[task_id] = task
        return task
        
    def execute_task(self, task_id: str):
        """Start executing a registered task."""
        if task_id not in self._task_registry:
            raise ValueError(f"Unknown task: {task_id}")
            
        task = self._task_registry[task_id]
        
        if task.state == TaskState.ACTIVE:
            return False  # Already running
            
        task.state = TaskState.ACTIVE
        future = self._executor.submit(self._perform_scrape, task)
        self._futures[task_id] = future
        return True
        
    def _perform_scrape(self, task: ScraperTask):
        """Internal method to perform scraping."""
        try:
            scraper_instance = task.scraper_type()
            collected = scraper_instance.scrape_plugins(max_pages=task.page_limit)
            
            task.result_data = collected
            task.item_count = len(collected)
            task.state = TaskState.FINISHED
            task.completed_at = datetime.now().isoformat()
            
        except Exception as error:
            task.state = TaskState.FAILED
            task.error_info = str(error)
            
    def get_task_info(self, task_id: str) -> Optional[Dict]:
        """Get current information about a task."""
        if task_id not in self._task_registry:
            return None
            
        task = self._task_registry[task_id]
        return {
            'state': task.state.value,
            'items': task.item_count,
            'timestamp': task.completed_at,
            'error': task.error_info
        }
        
    def get_all_status(self) -> Dict:
        """Get status of all registered tasks."""
        return {
            task_id: self.get_task_info(task_id)
            for task_id in self._task_registry
        }
        
    def retrieve_data(self, task_id: str) -> Dict:
        """Retrieve scraped data from a completed task."""
        if task_id not in self._task_registry:
            return {}
        return self._task_registry[task_id].result_data
        
    def shutdown(self):
        """Cleanup resources."""
        self._executor.shutdown(wait=False)
