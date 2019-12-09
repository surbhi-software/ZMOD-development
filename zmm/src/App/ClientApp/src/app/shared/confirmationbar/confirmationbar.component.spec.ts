import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfirmationbarComponent } from './confirmationbar.component';

describe('ConfirmationbarComponent', () => {
  let component: ConfirmationbarComponent;
  let fixture: ComponentFixture<ConfirmationbarComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ConfirmationbarComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfirmationbarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
