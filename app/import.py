from model.factory import SearchSystemFactory
from utils import PathHelper
import os
import csv
import logging
import json
import time
from datetime import datetime
from pathlib import Path

# Setup logging
def setup_logger():
    """Setup logger for import process"""
    log_dir = PathHelper.get_logs_dir()
    log_dir.mkdir(exist_ok=True)
    
    # Create timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"import_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    return logging.getLogger(__name__), log_file

# Performance monitoring class
class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.animal_start_time = None
        self.image_start_time = None
        self.total_images_processed = 0
        self.total_animals_processed = 0
        self.animal_processing_times = []
        self.image_processing_times = []
        
    def start_animal_processing(self, animal_name):
        """Start timing for animal processing"""
        self.animal_start_time = time.time()
        logger.info(f"Starting processing for animal: {animal_name}")
        
    def end_animal_processing(self, animal_name, images_processed):
        """End timing for animal processing and log performance"""
        if self.animal_start_time:
            processing_time = time.time() - self.animal_start_time
            self.animal_processing_times.append(processing_time)
            self.total_animals_processed += 1
            
            # Calculate throughput for this animal
            images_per_second = images_processed / processing_time if processing_time > 0 else 0
            
            logger.info(f"Completed {animal_name}: {images_processed} images in {processing_time:.2f}s "
                       f"({images_per_second:.2f} images/sec)")
            
    def start_image_processing(self):
        """Start timing for image processing"""
        self.image_start_time = time.time()
        
    def end_image_processing(self, success=True):
        """End timing for image processing"""
        if self.image_start_time:
            processing_time = time.time() - self.image_start_time
            self.image_processing_times.append(processing_time)
            self.total_images_processed += 1
            
            # Log every 10 images for performance monitoring
            if self.total_images_processed % 10 == 0:
                avg_image_time = sum(self.image_processing_times[-10:]) / min(10, len(self.image_processing_times[-10:]))
                images_per_second = 1 / avg_image_time if avg_image_time > 0 else 0
                logger.info(f"Performance update: {self.total_images_processed} images processed, "
                           f"avg {avg_image_time:.3f}s per image ({images_per_second:.2f} images/sec)")
                
    def get_performance_summary(self):
        """Get comprehensive performance summary"""
        total_time = time.time() - self.start_time
        
        if self.animal_processing_times:
            avg_animal_time = sum(self.animal_processing_times) / len(self.animal_processing_times)
            animals_per_second = self.total_animals_processed / total_time if total_time > 0 else 0
        else:
            avg_animal_time = 0
            animals_per_second = 0
            
        if self.image_processing_times:
            avg_image_time = sum(self.image_processing_times) / len(self.image_processing_times)
            images_per_second = self.total_images_processed / total_time if total_time > 0 else 0
        else:
            avg_image_time = 0
            images_per_second = 0
            
        return {
            'total_time': total_time,
            'total_animals_processed': self.total_animals_processed,
            'total_images_processed': self.total_images_processed,
            'avg_animal_processing_time': avg_animal_time,
            'avg_image_processing_time': avg_image_time,
            'animals_per_second': animals_per_second,
            'images_per_second': images_per_second,
            'animal_processing_times': self.animal_processing_times,
            'image_processing_times': self.image_processing_times
        }

# Initialize logger and performance monitor
logger, log_file = setup_logger()
performance_monitor = PerformanceMonitor()

# Initialize results tracking
import_results = {
    'start_time': datetime.now().isoformat(),
    'total_animals': 0,
    'successful_animals': 0,
    'failed_animals': 0,
    'total_images': 0,
    'successful_images': 0,
    'failed_images': 0,
    'animal_details': {},
    'errors': [],
    'performance': {}
}

search_system_factory = SearchSystemFactory()
search_system = search_system_factory.create()

dataset_dir = PathHelper.get_dataset_dir()
animal_names_path = dataset_dir / 'animal_names_famous.txt' # each line is an animal name
animal_images_dir = dataset_dir / 'animal_images' # each subfolder is an animal name, each image is an animal image
animal_captions_dir = dataset_dir / 'animal_captions' # each subfolder is an animal name, each file is an animal caption

logger.info("Starting import process")
logger.info(f"Dataset directory: {dataset_dir}")
logger.info(f"Animal names file: {animal_names_path}")
logger.info(f"Animal images directory: {animal_images_dir}")
logger.info(f"Animal captions directory: {animal_captions_dir}")

# Read animal names from file
try:
    with open(animal_names_path, 'r') as f:
        animal_names = f.read().splitlines()
    logger.info(f"Found {len(animal_names)} animal names to process")
except FileNotFoundError:
    logger.error(f"Animal names file not found: {animal_names_path}")
    import_results['errors'].append(f"Animal names file not found: {animal_names_path}")
    animal_names = []
except Exception as e:
    logger.error(f"Error reading animal names file: {e}")
    import_results['errors'].append(f"Error reading animal names file: {e}")
    animal_names = []

import_results['total_animals'] = len(animal_names)

# Loop through each animal name
for animal_name in animal_names:
    performance_monitor.start_animal_processing(animal_name)
    
    animal_images_path = animal_images_dir / animal_name
    animal_captions_path = animal_captions_dir / f"caption_{animal_name}.csv"
    
    animal_stats = {
        'animal_name': animal_name,
        'images_found': 0,
        'captions_found': 0,
        'successful_inserts': 0,
        'failed_inserts': 0,
        'processing_time': 0,
        'errors': []
    }

    # Check if the animal images directory exists
    if not animal_images_path.exists():
        error_msg = f"Animal images directory for {animal_name} does not exist: {animal_images_path}"
        logger.warning(error_msg)
        animal_stats['errors'].append(error_msg)
        import_results['failed_animals'] += 1
        import_results['animal_details'][animal_name] = animal_stats
        performance_monitor.end_animal_processing(animal_name, 0)
        continue

    # List image files in the directory
    try:
        image_files = [f for f in os.listdir(animal_images_path) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
        image_files.sort()
        animal_stats['images_found'] = len(image_files)
        logger.info(f"Found {len(image_files)} images for {animal_name}")
    except Exception as e:
        error_msg = f"Error listing images for {animal_name}: {e}"
        logger.error(error_msg)
        animal_stats['errors'].append(error_msg)
        import_results['failed_animals'] += 1
        import_results['animal_details'][animal_name] = animal_stats
        performance_monitor.end_animal_processing(animal_name, 0)
        continue

    # Read animal captions from CSV file
    captions = {}
    if animal_captions_path.exists():
        try:
            with open(animal_captions_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                for row in csv_reader:
                    if len(row) >= 2:
                        caption = row[1].strip().strip('"')
                        key = row[0].split('/')[-1].split('.')[0]
                        captions[key] = caption
            animal_stats['captions_found'] = len(captions)
            logger.info(f"Found {len(captions)} captions for {animal_name}")
        except Exception as e:
            error_msg = f"Error reading captions for {animal_name}: {e}"
            logger.error(error_msg)
            animal_stats['errors'].append(error_msg)
    else:
        error_msg = f"Caption file for {animal_name} does not exist: {animal_captions_path}"
        logger.warning(error_msg)
        animal_stats['errors'].append(error_msg)
        import_results['failed_animals'] += 1
        import_results['animal_details'][animal_name] = animal_stats
        performance_monitor.end_animal_processing(animal_name, 0)
        continue

    logger.info(f"Processing {animal_name}: {len(image_files)} images, {len(captions)} captions")

    # Loop through each image
    for index, image_filename in enumerate(image_files):
        performance_monitor.start_image_processing()
        
        if index < len(captions):
            try:
                caption = captions[image_filename.split('.')[0]]
                image_path = animal_images_path / image_filename

                animal_data = {
                    'animal': animal_name,
                    'caption': caption,
                    'image_path': 'dataset/' + str(image_path.relative_to(dataset_dir)).replace('\\', '/')
                }

                search_system.insert_record(animal_data)
                animal_stats['successful_inserts'] += 1
                import_results['successful_images'] += 1
                performance_monitor.end_image_processing(success=True)
                logger.debug(f"Successfully inserted {image_filename} for {animal_name}")
            except Exception as e:
                error_msg = f"Error inserting {image_filename} for {animal_name}: {e}"
                logger.error(error_msg)
                animal_stats['failed_inserts'] += 1
                animal_stats['errors'].append(error_msg)
                import_results['failed_images'] += 1
                performance_monitor.end_image_processing(success=False)
        else:
            error_msg = f"No caption found for image {image_filename}"
            logger.warning(error_msg)
            animal_stats['failed_inserts'] += 1
            animal_stats['errors'].append(error_msg)
            import_results['failed_images'] += 1
            performance_monitor.end_image_processing(success=False)

    import_results['total_images'] += len(image_files)
    animal_stats['processing_time'] = performance_monitor.animal_processing_times[-1] if performance_monitor.animal_processing_times else 0
    import_results['animal_details'][animal_name] = animal_stats
    
    if animal_stats['successful_inserts'] > 0:
        import_results['successful_animals'] += 1
    else:
        import_results['failed_animals'] += 1

    performance_monitor.end_animal_processing(animal_name, len(image_files))

# Get performance summary
performance_summary = performance_monitor.get_performance_summary()
import_results['performance'] = performance_summary

# Finalize results
import_results['end_time'] = datetime.now().isoformat()
import_results['duration'] = (datetime.fromisoformat(import_results['end_time']) - 
                             datetime.fromisoformat(import_results['start_time'])).total_seconds()

# Save results to file
results_dir = "./results"
os.makedirs(results_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_file = results_dir / f"import_results_{timestamp}.json"

try:
    with open(results_file, 'w') as f:
        json.dump(import_results, f, indent=2)
    logger.info(f"Import results saved to: {results_file}")
except Exception as e:
    logger.error(f"Error saving results file: {e}")

# Log final summary with performance metrics
logger.info("=" * 60)
logger.info("IMPORT SUMMARY")
logger.info("=" * 60)
logger.info(f"Total animals: {import_results['total_animals']}")
logger.info(f"Successful animals: {import_results['successful_animals']}")
logger.info(f"Failed animals: {import_results['failed_animals']}")
logger.info(f"Total images: {import_results['total_images']}")
logger.info(f"Successful images: {import_results['successful_images']}")
logger.info(f"Failed images: {import_results['failed_images']}")
logger.info("=" * 60)
logger.info("PERFORMANCE METRICS")
logger.info("=" * 60)
logger.info(f"Total duration: {performance_summary['total_time']:.2f} seconds")
logger.info(f"Average animal processing time: {performance_summary['avg_animal_processing_time']:.2f} seconds")
logger.info(f"Average image processing time: {performance_summary['avg_image_processing_time']:.3f} seconds")
logger.info(f"Throughput - Animals per second: {performance_summary['animals_per_second']:.2f}")
logger.info(f"Throughput - Images per second: {performance_summary['images_per_second']:.2f}")
logger.info("=" * 60)
logger.info(f"Log file: {log_file}")
logger.info(f"Results file: {results_file}")
logger.info("=" * 60)

print(f"\nImport completed! Check logs at: {log_file}")
print(f"Results saved to: {results_file}")
print(f"Performance: {performance_summary['images_per_second']:.2f} images/sec, {performance_summary['animals_per_second']:.2f} animals/sec")
