import { Component, OnInit, EventEmitter, Output, ViewChild } from '@angular/core';
import { ApiRoutes, HttpService, UtilService, AlertMessages } from '../../shared';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-cumulocity',
  templateUrl: './cumulocity.component.html',
  styleUrls: ['./cumulocity.component.scss']
})
export class CumulocityComponent implements OnInit {
  public client;
  public displayedColumns: string[] = ['id', 'name', 'model', 'status', 'action'];
  public dataSourceDevices: any;
  public selectedDevice: any = {};
  public username = '';
  public password = '';
  public hide;
  public listDevice;
  public listFile;
  public tenant = '';
  public dataSourceFiles: any;
  public aggregationOptions: string[] = ['MINUTELY', 'HOURLY', 'DAILY'];
  public dataPoints: object[] = [
    {
      'unit': 'uT',
      'name': 'compassY',
      'type': 'c8y_Compass'
    },
    {
      'unit': 'lux',
      'name': 'lux',
      'type': 'c8y_Luxometer'
    },
    {
      'unit': '°/s',
      'name': 'gyroZ',
      'type': 'c8y_Gyroscope'
    },
    {
      'unit': 'G',
      'name': 'accelerationZ',
      'type': 'c8y_Acceleration'
    },
    {
      'unit': 'G',
      'name': 'accelerationY',
      'type': 'c8y_Acceleration'
    },
    {
      'unit': 'uT',
      'name': 'compassZ',
      'type': 'c8y_Compass'
    },
    {
      'unit': '°/s',
      'name': 'gyroX',
      'type': 'c8y_Gyroscope'
    },
    {
      'unit': 'G',
      'name': 'accelerationX',
      'type': 'c8y_Acceleration'
    },
    {
      'unit': '°/s',
      'name': 'gyroY',
      'type': 'c8y_Gyroscope'
    },
    {
      'unit': 'uT',
      'name': 'compassX',
      'type': 'c8y_Compass'
    },
    {
      'unit': 'dBm',
      'name': 'rssi',
      'type': 'c8y_SignalStrengthWifi'
    }
  ];
  @Output() cumulocitySuccess = new EventEmitter<any>();

  public seriesFilter: any = {
    dateFrom: new Date(),
    timeFromH: 11,
    timeFromM: 30,
    dateTo: new Date(),
    timeToH: 12,
    timeToM: 30,
    source: this.selectedDevice.id,
    pageSize: 1440,
    revert: true,
    aggregationType: 'MINUTELY',
    series: ['c8y_Acceleration.accelerationY', 'c8y_Acceleration.accelerationX', 'c8y_Acceleration.accelerationZ']
  };
  @ViewChild('seriesForm') seriesForm;
  public isLoading = false;
  public isContentLoading = false;
  public headers: any = {};
  public c8y: any = {};
  constructor(private apiService: HttpService, private utilService: UtilService) { }

  public getSettings() {
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.settings)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        console.log(response);
        this.c8y = this.utilService.getSettingsObject('C8Y', response);
        console.log(this.c8y);
        if (this.c8y && this.c8y.url) {
          this.login({ valid: true });
        } else {
          this.utilService.alert('Cumulocity credentials not defined.');
        }
      });
  }

  public login(loginData: any) {
    this.dataSourceDevices = [];
    this.dataSourceFiles = [];
    this.listDevice = false;
    this.listFile = false;
    if (loginData.valid) {
      console.log(this.c8y);
      this.headers.Authorization = `Basic ${btoa(`${this.c8y.tenantID}/${this.c8y.username}:${this.c8y.password}`)}`;
      this.listDevices();
    }
  }

  public listDevices() {
    this.listDevice = true;
    this.listFile = false;
    const options = {
      params: {
        pageSize: 100,
        withTotalPages: true,
        type: 'c8y_SensorPhone'
      },
      headers: this.headers
    };
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, `${this.c8y.url}/inventory/managedObjects`, options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        console.log(response);
        this.dataSourceDevices = response.managedObjects;
      }, responseError => {
        console.log(responseError);
      });
  }

  public listFiles() {
    this.listFile = true;
    this.listDevice = false;
    const options = {
      params: {
        pageSize: 100,
        withTotalPages: true,
        type: 'image/png'
      },
      headers: this.headers
    };
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, `${this.c8y.url}/inventory/binaries`, options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        console.log(response);
        this.dataSourceFiles = response.managedObjects;
      }, responseError => {
        console.log(responseError);
      });
  }

  public saveCumulocityImage(data: any) {
    const options = {
      headers: this.headers,
      responseType: 'blob'
    };
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, data.self, options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        this.uploadResponseData(response, `${data.name}.png`);
      }, responseError => {
        console.log(responseError);
      });
  }

  public listSeries() {
    const options = {
      params: this.seriesFilter,
      headers: this.headers
    };
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, `${this.c8y.url}/measurement/measurements/series`, options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        console.log(response);
        if (response && response.series.length) {
          const jsonData = JSON.stringify(response);
          const blobData = new Blob([jsonData], { type: 'octet/stream' });
          this.uploadResponseData(blobData, `${this.seriesFilter.fileName}.json`);
        } else {
          this.utilService.alert('No data available');
        }
      });
  }

  public uploadResponseData(fileData: any, fileName: string) {
    const formData = new FormData();
    formData.append('file', fileData, fileName);
    const options = {
      body: formData
    };
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.data, options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        console.log(response);
        this.cumulocitySuccess.emit(response);
        this.selectedDevice = {};
      }, err => {
        console.log(err);
      });
  }

  public selectDevice(device: any) {
    this.selectedDevice = device;
    this.seriesFilter.source = this.selectedDevice.id;
    console.log(device);
    this.seriesFilter.fileName = '';
  }

  public submitSeriesParameters() {
    console.log(this.seriesFilter);
    this.seriesForm.submitted = true;
    if (this.seriesForm.valid) {
      if (!this.seriesFilter.aggregationType) {
        delete this.seriesFilter.aggregationType;
      }

      const dateFrom = new Date(this.seriesFilter.dateFrom);
      dateFrom.setHours(this.seriesFilter.timeFromH);
      dateFrom.setMinutes(this.seriesFilter.timeFromM);
      this.seriesFilter.dateFrom = dateFrom.toISOString();

      const dateTo = new Date(this.seriesFilter.dateTo);
      dateTo.setHours(this.seriesFilter.timeToH);
      dateTo.setMinutes(this.seriesFilter.timeToM);
      this.seriesFilter.dateTo = dateTo.toISOString();
      this.listSeries();
    }
  }

  ngOnInit() {
    this.getSettings();
  }

}