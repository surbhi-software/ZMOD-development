import { Component, OnInit, Input, EventEmitter, Output, ViewChild } from '@angular/core';

@Component({
selector: 'app-automl-parameters-form',
templateUrl: './automl-parameters-form.component.html',
styleUrls: ['./automl-parameters-form.component.scss']
})
export class AutomlParametersFormComponent implements OnInit {
@Input() option: any;
@Output() close = new EventEmitter<any>();
@Output() selected = new EventEmitter<any>();
data: any = [];
formData: any = {};
public isLoading = false;
public scoringOptions = [
  'accuracy',
  'adjusted_rand_score',
  'average_precision',
  'balanced_accuracy',
  'f1',
  'f1_macro',
  'f1_micro',
  'f1_samples',
  'f1_weighted',
  'neg_log_loss',
  'precision',
  'precision_macro',
  'precision_micro',
  'precision_samples',
  'precision_weighted',
  'recall',
  'recall_macro',
  'recall_micro',
  'recall_samples',
  'recall_weighted',
  'roc_auc',
  'neg_median_absolute_error',
  'neg_mean_absolute_error',
  'neg_mean_squared_error',
  'r2'
];
public algorithmOptions = [];
public algorithmOptionsAnomaly = [];
@ViewChild('automlTrainingParamsForm') automlTrainingParamsForm;

constructor() { }

closeForm() {
  this.close.emit(true);
}

submit() {
  this.automlTrainingParamsForm.submitted = true;
  if (this.automlTrainingParamsForm.valid) {
    this.selected.emit(this.formData);
  }
}

ngOnInit() {
  this.algorithmOptions = this.option.algorithmTypes[this.option.problem_type];
  this.algorithmOptionsAnomaly = this.option.algorithmTypes['Anomaly'];
  this.formData = {
    generation: 10, // optional
    population_size: 25, // optional
    // offspring_size: 1, // optional
    // mutation_rate: 1, // optional
    // crossover_rate: -2, // optional
    // scoring: 'accuracy', // dropdown optional
    // cv: 1, // optional
    // subsample: 1, // optional
    // n_jobs: 1, // optional
    // max_time_mins: 1, // optional
    // max_eval_time_mins: 1, // optional
    // random_state: 1, // optional
    // warm_start: false, // (boolean, optional)
    // early_stop: 1 //(integer, optional)
  };
}

}
