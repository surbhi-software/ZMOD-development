import { Component, OnInit, ViewChild, Output, EventEmitter, Input } from '@angular/core';
import { ApiRoutes, HttpService } from '../../../shared';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-welding-config-form',
  templateUrl: './welding-config-form.component.html',
  styleUrls: ['./welding-config-form.component.scss']
})
export class WeldingConfigFormComponent implements OnInit {

  @Output() close = new EventEmitter<any>();
  @Output() selected = new EventEmitter<any>();
  @Input() baseImageInfo: any = {};
  data: any = {};
  formData: any = {};
  public isLoading = false;
  public isContentLoading = false;

  @ViewChild('thisForm') thisForm;

  gapOptions = [1, 2, 3, 4, 5];
  x_varOptions = [1, 2, 3, 4];
  y_varOptions = [1, 2, 3];
  resizeOptions = [15, 16, 17, 18];
  num_platesOptions = [2, 3, 4];
  colorOptions = [
    {
      name: 'Black',
      hexCode: '#000000',
      rgb: [0, 0, 0]
    },
    {
      name: 'White',
      hexCode: '#FFFFFF',
      rgb: [255, 255, 255]
    },
    {
      name: 'Red',
      hexCode: '#FF0000',
      rgb: [255, 0, 0]
    },
    {
      name: 'Lime',
      hexCode: '#00FF00',
      rgb: [0, 255, 0]
    },
    {
      name: 'Blue',
      hexCode: '#0000FF',
      rgb: [0, 0, 255]
    },
    {
      name: 'Yellow',
      hexCode: '#FFFF00',
      rgb: [255, 255, 0]
    },
    {
      name: 'Cyan / Aqua',
      hexCode: '#00FFFF',
      rgb: [0, 255, 255]
    },
    {
      name: 'Magenta / Fuchsia',
      hexCode: '#FF00FF',
      rgb: [255, 0, 255]
    },
    {
      name: 'Silver',
      hexCode: '#C0C0C0',
      rgb: [192, 192, 192]
    },
    {
      name: 'Gray',
      hexCode: '#808080',
      rgb: [128, 128, 128]
    },
    {
      name: 'Maroon',
      hexCode: '#800000',
      rgb: [128, 0, 0]
    },
    {
      name: 'Olive',
      hexCode: '#808000',
      rgb: [128, 128, 0]
    },
    {
      name: 'Green',
      hexCode: '#008000',
      rgb: [0, 128, 0]
    },
    {
      name: 'Purple',
      hexCode: '#800080',
      rgb: [128, 0, 128]
    },
    {
      name: 'Teal',
      hexCode: '#008080',
      rgb: [0, 128, 128]
    },
    {
      name: 'Navy',
      hexCode: '#000080',
      rgb: [0, 0, 128]
    }
  ]
  // https://www.rapidtables.com/web/color/RGB_Color.html Color names ref
  constructor(private apiService: HttpService) { }
  closeForm() {
    this.close.emit(true);
  }
  submit() {
    this.thisForm.submitted = true;
    if (this.thisForm.valid) {
      this.selected.emit(this.formData);
    }
  }

  generateImages() {
    this.thisForm.submitted = true;
    if (this.thisForm.valid) {
      this.formData.generateImages = true;
      this.selected.emit(this.formData);
    }
  }

  ngOnInit() {
    console.log(this.baseImageInfo);
    this.formData = this.baseImageInfo.configParams;
  }


}

