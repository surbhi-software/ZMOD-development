import { Component, OnInit, Input, EventEmitter, Output, ViewChild, } from '@angular/core';

@Component({
  selector: 'app-display-config-form',
  templateUrl: './display-config-form.component.html',
  styleUrls: ['./display-config-form.component.scss']
})
export class DisplayConfigFormComponent implements OnInit {
  @Input() option: any;
  @Output() close = new EventEmitter<any>();
  @Output() selected = new EventEmitter<any>();
  data: any = [];
  formData: any = {};
  public isLoading = false;
  public gpuOptions = [{ id: 'NO_GPU', name: 'NO GPU' }];
  @ViewChild('displayConfigForm') displayConfigForm;
  constructor() { }

  ngOnInit() {
    const listOfInstances = this.option;
    if (listOfInstances && listOfInstances.length) {
      const gpuList = listOfInstances.filter((value: any) => (value.type === 'GPU'));
      if (gpuList && gpuList.length) {
        this.gpuOptions = this.gpuOptions.concat(gpuList);
      }
    }
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
