import { Component, OnInit, Input, EventEmitter, Output, ViewChild } from '@angular/core';
import { CronOptions } from 'cron-editor/lib/CronOptions';

@Component({
  selector: 'app-training-parameters-form',
  templateUrl: './training-parameters-form.component.html',
  styleUrls: ['./training-parameters-form.component.scss']
})
export class TrainingParametersFormComponent implements OnInit {
  @Input() option: any;
  @Output() close = new EventEmitter<any>();
  @Output() selected = new EventEmitter<any>();
  data: any = [];
  formData: any = {};
  public isLoading = false;
  public lossOptions = ['binary_crossentropy', 'categorical_crossentropy', 'MAE', 'RMSE', 'MSE'];
  public metricsOptions = ['accuracy', 'f1', 'MAE', 'RMSE', 'MSE'];
  public optimizerOptions = ['SGD', 'RMSprop', 'Adagrad', 'Adam', 'Adamax'];
  public problemTypeOptions = ['classification', 'regression'];
  public scriptOutputOptions = ['NA', 'IMAGE', 'DATA'];
  public cronExpression = '0 15 0/1 1/1 * ? *';
  public isCronDisabled = false;
  public cronOptions: CronOptions = {
    formInputClass: 'form-control cron-editor-input',
    formSelectClass: 'form-control cron-editor-select',
    formRadioClass: 'cron-editor-radio',
    formCheckboxClass: 'cron-editor-checkbox',
    defaultTime: '10:00:00',
    use24HourTime: true,
    hideMinutesTab: false,
    hideHourlyTab: false,
    hideDailyTab: false,
    hideWeeklyTab: false,
    hideMonthlyTab: false,
    hideYearlyTab: true,
    hideAdvancedTab: true,
    hideSeconds: true,
    removeSeconds: false,
    removeYears: false
  };
  @ViewChild('trainingForm') trainingForm;

  constructor() { }

  closeForm() {
    this.close.emit(true);
  }

  submit() {
    this.trainingForm.submitted = true;
    if (this.trainingForm.valid) {
      this.selected.emit(this.formData);
    }
  }

  ngOnInit() {
    this.formData = {
      batchSize: 15,
      epoch: 100,
      stepPerEpoch: 10,
      learningRate: .001,
      loss: 'categorical_crossentropy',
      metrics: ['accuracy', 'f1'],
      optimizer: 'Adam',
      testSize: .3,
      scriptOutput: 'NA'
    };
    this.formData.recurrence = 'ONE_TIME';
    this.formData.cronExpression = '0 15 0/1 1/1 * ? *';
  }

}
