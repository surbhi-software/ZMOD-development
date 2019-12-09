import { Component, OnInit } from '@angular/core';
import { UtilService } from '../../shared';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.scss']
})
export class FooterComponent implements OnInit {

  version: string;

  constructor(private utilService: UtilService) { }

  ngOnInit() {
    this.version = this.utilService.getAppVersion();
  }

}
