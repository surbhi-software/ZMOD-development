import { Component, OnInit, Input, EventEmitter, Output, ViewChild, ViewEncapsulation } from '@angular/core';
import { CronOptions } from 'cron-editor/lib/CronOptions';

@Component({
  selector: 'app-excute-form',
  templateUrl: './excute-form.component.html',
  styleUrls: ['./excute-form.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ExcuteFormComponent implements OnInit {
  @Input() option: any;
  @Output() close = new EventEmitter<any>();
  @Output() selected = new EventEmitter<any>();
  data: any = [];
  formData: any = {};
  public isLoading = false;
  @ViewChild('displayConfigForm') displayConfigForm;

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

  constructor() { }

  ngOnInit() {
    console.log(this.option);
    this.formData.recurrence = 'ONE_TIME';
    this.formData.cronExpression = '0 15 0/1 1/1 * ? *';
  }
  closeForm() {
    this.close.emit(true);
  }
  submit() {
    this.displayConfigForm.submitted = true;
    if (this.displayConfigForm.valid) {
      this.selected.emit(this.formData);
    }
  }
}
