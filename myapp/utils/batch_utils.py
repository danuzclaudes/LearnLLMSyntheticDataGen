import concurrent.futures
import threading

DEFAULT_MAX_CONCURRENT_BATCHES = 3


class BatchProcessor:
    def __init__(self):
        self.semaphore = threading.Semaphore(DEFAULT_MAX_CONCURRENT_BATCHES)

    def process_batches(
        self,
        num_of_batches: int,
        batch_function,
        **kwargs,
    ):
        """
        Generic method to process batches in parallel with a semaphore.

        Parameters:
            num_of_batches (int): Total number of batches.
            batch_function (callable): Function to generate each batch.
            **kwargs: Keyword arguments for `batch_function`.

        Returns:
            list: Combined results from all batches.
        """
        results = []

        def _process_with_semaphore(batch_index):
            """
            Wrapper to enforce semaphore control for each batch process.
            """
            with self.semaphore:  # Rate limiting via semaphore
                return batch_function(batch_index, **kwargs)

        # Use a ThreadPoolExecutor for parallel batch processing
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all batch tasks
            future_to_batch = {
                executor.submit(_process_with_semaphore, batch_index): batch_index
                for batch_index in range(num_of_batches)
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_batch):
                try:
                    results.extend(future.result())
                except Exception as e:
                    batch_index = future_to_batch[future]
                    print(f"Error processing batch {batch_index}: {e}")

        return results
